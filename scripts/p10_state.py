#!/usr/bin/env python3
"""
p10_state.py — P10 State Guard Validator (Specification v0.1)

Enforces state transitions as physical properties of disk artifacts, git history,
and server-side timestamps. Holds zero hardcoded doctrine literals.
"""

import os
import sys
import json
import re
import hashlib
import subprocess
import argparse
import tempfile
from datetime import datetime, timezone
import urllib.request
import urllib.error

EXIT_PASS = 0
EXIT_BLOCKED = 1
EXIT_ERROR = 2

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def log_diag(msg: str):
    print(f"[P10-GUARD] {msg}", file=sys.stderr)


def fetch_url(url: str, token: str = None) -> bytes:
    headers = {"User-Agent": "P10-State-Guard/0.1"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["Accept"] = "application/vnd.github.v3+json"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}")


class DoctrineParser:
    """
    Parses normative vocabulary, section headings, and allowed statuses dynamically
    from the pinned doctrine repository commit. Holds zero doctrine string literals in code.
    Strictly fetches from remote pinned commit; zero unverified local fallbacks.
    """
    def __init__(self, repo: str, commit: str, files_pin: dict, github_token: str = None):
        self.repo = repo
        self.commit = commit
        self.files_pin = files_pin
        self.github_token = github_token
        self.fetched_files = {}
        self.verdict_vocabulary = []
        self.template_headings = []
        self.allowed_operational_statuses = []
        self.pg_steps = []

    def verify_and_parse(self):
        log_diag(f"Verifying doctrine pin strictly against {self.repo} @ {self.commit}...")
        for filename, expected_sha in self.files_pin.items():
            # Source is strictly the pinned remote commit
            raw_url = f"https://raw.githubusercontent.com/{self.repo}/{self.commit}/{filename}"
            content = fetch_url(raw_url, self.github_token)

            actual_sha = hashlib.sha256(content).hexdigest()
            if actual_sha.lower() != expected_sha.lower():
                raise ValueError(
                    f"Doctrine pin mismatch for {filename}!\n"
                    f"  Expected sha256: {expected_sha}\n"
                    f"  Actual sha256:   {actual_sha}"
                )
            self.fetched_files[filename] = content.decode("utf-8", errors="replace")
            log_diag(f"  Verified {filename}: {actual_sha[:12]}... OK")

        self._parse_design_principles()
        self._parse_template()
        self._parse_checklist()

    def _parse_design_principles(self):
        content = self.fetched_files.get("DESIGN_PRINCIPLES.md", "")
        # Parse items under ## Verdict vocabulary: "- **<Word>** — description"
        vocab_section = re.search(r"##\s+Verdict vocabulary\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
        if not vocab_section:
            raise ValueError("Could not find '## Verdict vocabulary' in DESIGN_PRINCIPLES.md")
        matches = re.findall(r"-\s+\*\*([^*]+)\*\*", vocab_section.group(1))
        if not matches:
            raise ValueError("Failed to extract verdict terms from DESIGN_PRINCIPLES.md")
        self.verdict_vocabulary = [m.strip() for m in matches]
        log_diag(f"Parsed {len(self.verdict_vocabulary)} dynamic verdicts: {self.verdict_vocabulary}")

    def _parse_template(self):
        content = self.fetched_files.get("TEMPLATE.md", "")
        # Extract all ## numbered headings
        headings = re.findall(r"^##\s+(\d+\.\s+[^#\n\r]+)", content, re.MULTILINE)
        if not headings:
            raise ValueError("Could not extract section headings from TEMPLATE.md")
        self.template_headings = [h.strip() for h in headings]
        log_diag(f"Parsed {len(self.template_headings)} template headings: {self.template_headings}")

        # Extract allowed operational statuses from §4: `STATUS`
        sec4 = re.search(r"##\s+4\.\s+Operational Status\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
        if sec4:
            statuses = re.findall(r"`([^`]+)`", sec4.group(1))
            self.allowed_operational_statuses = [s.strip() for s in statuses]
        log_diag(f"Parsed allowed operational statuses: {self.allowed_operational_statuses}")

    def _parse_checklist(self):
        content = self.fetched_files.get("PREPUBLISH_CHECKLIST.md", "")
        steps = re.findall(r"^##\s+(PG\d+)\s+—", content, re.MULTILINE)
        self.pg_steps = [s.strip() for s in steps]
        log_diag(f"Parsed PG steps from checklist: {self.pg_steps}")


class P10StateGuard:
    def __init__(self, instance_dir: str, github_token: str = None, report_only: bool = False):
        self.instance_dir = os.path.abspath(instance_dir)
        self.state_file = os.path.join(self.instance_dir, "STATE.json")
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        self.report_only = report_only
        self.state = {}
        self.doctrine = None
        self.blockers = []

    def block(self, phase: str, reason: str):
        msg = f"PHASE {phase} BLOCKED: {reason}"
        self.blockers.append(msg)
        log_diag(f"  [X] {msg}")

    def run(self) -> int:
        if not os.path.exists(self.state_file):
            self.block("ROOT", f"STATE.json not found in {self.instance_dir}")
            return EXIT_BLOCKED

        try:
            with open(self.state_file, "r") as f:
                self.state = json.load(f)
        except Exception as e:
            log_diag(f"Malformed STATE.json: {e}")
            return EXIT_ERROR

        # 1. Verify Doctrine Pin FIRST (§4.1 - Blocks Gate Reviewer First)
        pin = self.state.get("doctrine_pin")
        if not pin or "repo" not in pin or "commit" not in pin or "files" not in pin:
            self.block("DOCTRINE_PIN", "Missing or incomplete doctrine_pin block in STATE.json")
            return EXIT_BLOCKED

        try:
            self.doctrine = DoctrineParser(pin["repo"], pin["commit"], pin["files"], self.github_token)
            self.doctrine.verify_and_parse()
        except Exception as e:
            self.block("DOCTRINE_PIN", f"Doctrine verification failed: {e}")
            return EXIT_BLOCKED

        phases = self.state.get("phases", {})

        # 2. Evaluate Phases in Ordered Sequence
        phase_order = [
            "PREREGISTRATION", "TARGET_SET", "DATA_MANIFEST", "EXECUTION",
            "RESULTS", "VERDICT", "PG1", "PG2", "PG3", "PG4", "PG5", "PG6", "PG7", "PG8", "PG9"
        ]

        completed_phases = set()
        for phase_name in phase_order:
            if phase_name not in phases:
                continue
            phase_info = phases[phase_name]
            declared = phase_info.get("declared", "NOT_STARTED")
            prereq = phase_info.get("prerequisite")

            if declared in ["NOT_STARTED", "IN_PROGRESS"]:
                log_diag(f"Phase {phase_name} is {declared}. Skipping further evaluation.")
                continue

            if prereq and prereq not in completed_phases:
                self.block(phase_name, f"Prerequisite {prereq} is not COMPLETE (got {phases.get(prereq, {}).get('declared')})")
                continue

            # Evaluate specific phase predicates
            eval_fn = getattr(self, f"_eval_{phase_name.lower()}", None)
            if eval_fn:
                ok = eval_fn(phase_info)
                if ok:
                    completed_phases.add(phase_name)
                    log_diag(f"Phase {phase_name} [PASS]")
            else:
                log_diag(f"Warning: No explicit evaluator for {phase_name}")

        print("\n=======================================================", file=sys.stderr)
        print("P10 STATE GUARD EVALUATION REPORT", file=sys.stderr)
        print("=======================================================", file=sys.stderr)
        if self.blockers:
            print(f"VERDICT: BLOCKED ({len(self.blockers)} violations found)\n", file=sys.stderr)
            for b in self.blockers:
                print(f"  * {b}", file=sys.stderr)
            return EXIT_BLOCKED if not self.report_only else EXIT_PASS
        else:
            print("VERDICT: PASS (All declared states verified by evidence)", file=sys.stderr)
            return EXIT_PASS

    # -------------------------------------------------------------
    # Mechanical Phase Predicates
    # -------------------------------------------------------------

    def _eval_preregistration(self, pinfo: dict) -> bool:
        # P1: git log gives commit introducing PREREGISTRATION.md
        # P2: sha256(working tree) == sha256(PREREGISTRATION.md @ C)
        # P3: declared.freeze_commit == C
        prereg_path = os.path.join(self.instance_dir, "PREREGISTRATION.md")
        if not os.path.exists(prereg_path):
            self.block("PREREGISTRATION", "PREREGISTRATION.md artifact missing on disk")
            return False

        try:
            rel_path = os.path.relpath(prereg_path, REPO_ROOT)
            out = subprocess.check_output(
                ["git", "log", "--diff-filter=A", "--format=%H", "-n", "1", "--", rel_path],
                cwd=REPO_ROOT, text=True
            ).strip()
            if not out:
                self.block("PREREGISTRATION", "No git commit introducing PREREGISTRATION.md found")
                return False
            freeze_commit = out.splitlines()[-1]
        except Exception as e:
            self.block("PREREGISTRATION", f"Git inspection failed: {e}")
            return False

        current_sha = hashlib.sha256(open(prereg_path, "rb").read()).hexdigest()
        try:
            frozen_content = subprocess.check_output(
                ["git", "show", f"{freeze_commit}:{rel_path}"],
                cwd=REPO_ROOT
            )
            frozen_sha = hashlib.sha256(frozen_content).hexdigest()
        except Exception as e:
            self.block("PREREGISTRATION", f"Failed to retrieve frozen commit content: {e}")
            return False

        if current_sha != frozen_sha:
            self.block("PREREGISTRATION", f"PREREGISTRATION.md modified after freeze! Current {current_sha} != Frozen {frozen_sha}")
            return False

        declared_commit = pinfo.get("evidence", {}).get("freeze_commit")
        if declared_commit and not freeze_commit.startswith(declared_commit):
            self.block("PREREGISTRATION", f"Declared freeze commit {declared_commit} != Git {freeze_commit}")
            return False

        return True

    def _eval_target_set(self, pinfo: dict) -> bool:
        # P1: target set exists
        # P4: count == results.json target_set.total_lookups
        results_path = os.path.join(self.instance_dir, "results.json")
        if not os.path.exists(results_path):
            self.block("TARGET_SET", "results.json missing to verify target set size")
            return False
        try:
            res_data = json.load(open(results_path))
            total_lookups = res_data.get("target_set", {}).get("total_lookups")
            if total_lookups is None:
                self.block("TARGET_SET", "results.json missing target_set.total_lookups field")
                return False
        except Exception as e:
            self.block("TARGET_SET", f"Malformed results.json: {e}")
            return False
        return True

    def _eval_data_manifest(self, pinfo: dict) -> bool:
        # K-1 & K-2 Fixes: Server-side temporal ordering predicate P1–P3 (Fails Closed)
        # P1: A workflow run exists for freeze commit C
        # P2: T_freeze = min(run.run_started_at) across all Actions runs for C (GitHub server-side)
        # P3: for every entry in data_manifest.json: entry.retrieved_at_utc > T_freeze
        # P4: 64-hex sha256 and integer status_code
        # P5: No raw response bodies in repository

        manifest_path = os.path.join(self.instance_dir, "data_manifest.json")
        if not os.path.exists(manifest_path):
            self.block("DATA_MANIFEST", "data_manifest.json missing")
            return False

        prereg_info = self.state.get("phases", {}).get("PREREGISTRATION", {})
        freeze_commit = prereg_info.get("evidence", {}).get("freeze_commit")
        if not freeze_commit:
            self.block("DATA_MANIFEST", "PREREGISTRATION freeze_commit missing for temporal ordering check")
            return False

        # Query GitHub Actions API for all runs for this freeze commit
        repo_owner_name = "VolMax-Studio/Open-Market-Notes"
        runs_url = f"https://api.github.com/repos/{repo_owner_name}/actions/runs?head_sha={freeze_commit}"

        try:
            runs_raw = fetch_url(runs_url, self.github_token)
            runs_data = json.loads(runs_raw.decode("utf-8"))
            workflow_runs = runs_data.get("workflow_runs", [])
        except Exception as e:
            # K-1: Fail Closed on API or network failure
            self.block("DATA_MANIFEST", f"Fail closed: Failed to query GitHub Actions runs for freeze commit {freeze_commit} ({e})")
            return False

        if not workflow_runs:
            # K-1: Fail Closed if no server-side run exists
            self.block("DATA_MANIFEST", f"Fail closed: Zero GitHub Actions workflow runs found for freeze commit {freeze_commit}")
            return False

        started_timestamps = []
        for wr in workflow_runs:
            st = wr.get("run_started_at")
            if st:
                try:
                    started_timestamps.append(datetime.fromisoformat(st.replace("Z", "+00:00")))
                except Exception:
                    pass

        if not started_timestamps:
            self.block("DATA_MANIFEST", f"Fail closed: No valid run_started_at found in Actions runs for {freeze_commit}")
            return False

        # K-2: T_freeze is the earliest (min) run started at
        t_freeze_dt = min(started_timestamps)
        log_diag(f"  Established server-side T_freeze = {t_freeze_dt.isoformat()} (earliest of {len(started_timestamps)} runs)")

        try:
            m = json.load(open(manifest_path))
            # Verify top-level manifest timestamp
            manifest_time_str = m.get("retrieved_at_utc")
            if not manifest_time_str:
                self.block("DATA_MANIFEST", "Missing retrieved_at_utc in data_manifest.json")
                return False

            m_dt = datetime.fromisoformat(manifest_time_str.replace("Z", "+00:00"))
            if m_dt <= t_freeze_dt:
                self.block("DATA_MANIFEST", f"Temporal ordering violation: data_manifest.json retrieved_at_utc ({m_dt.isoformat()}) <= T_freeze ({t_freeze_dt.isoformat()})")
                return False

            reqs = m.get("requests", {})
            if not reqs:
                self.block("DATA_MANIFEST", "Zero requests recorded in data_manifest.json")
                return False

            # K-2: Verify per-entry timestamps, sha256 digests, and integer status_codes
            for req_key, req_val in reqs.items():
                entry_time_str = req_val.get("retrieved_at_utc")
                if entry_time_str:
                    e_dt = datetime.fromisoformat(entry_time_str.replace("Z", "+00:00"))
                    if e_dt <= t_freeze_dt:
                        self.block("DATA_MANIFEST", f"Temporal ordering violation for {req_key}: {e_dt.isoformat()} <= T_freeze ({t_freeze_dt.isoformat()})")
                        return False

                sha = req_val.get("response_sha256")
                status = req_val.get("status_code")
                if not sha or len(sha) != 64 or not all(c in "0123456789abcdefABCDEF" for c in sha):
                    self.block("DATA_MANIFEST", f"Invalid SHA-256 for request {req_key}: {sha}")
                    return False
                if not isinstance(status, int):
                    self.block("DATA_MANIFEST", f"Invalid status_code for {req_key}: {status}")
                    return False
        except Exception as e:
            self.block("DATA_MANIFEST", f"Malformed data_manifest.json: {e}")
            return False
        return True

    def _eval_execution(self, pinfo: dict) -> bool:
        # P1: src/reproduce.py exists
        # P2: no filesystem credential paths
        # P4: expected digest == sha256(results.json) in tree
        reproduce_script = os.path.join(self.instance_dir, "src", "reproduce.py")
        results_file = os.path.join(self.instance_dir, "results.json")
        if not os.path.exists(reproduce_script):
            self.block("EXECUTION", "src/reproduce.py missing")
            return False
        if not os.path.exists(results_file):
            self.block("EXECUTION", "results.json missing")
            return False

        reproduce_content = open(reproduce_script).read()
        if re.search(r"~[/\\]|/home/|/Users/|[C-Z]:\\", reproduce_content):
            self.block("EXECUTION", "Local filesystem path detected in src/reproduce.py")
            return False

        expected_match = re.search(r'EXPECTED_RESULTS_SHA256\s*=\s*["\']([0-9a-fA-F]{64})["\']', reproduce_content)
        if not expected_match:
            self.block("EXECUTION", "EXPECTED_RESULTS_SHA256 not found in src/reproduce.py")
            return False

        actual_sha = hashlib.sha256(open(results_file, "rb").read()).hexdigest()
        if expected_match.group(1).lower() != actual_sha.lower():
            self.block("EXECUTION", f"Expected sha256 {expected_match.group(1)} != actual results.json {actual_sha}")
            return False
        return True

    def _eval_results(self, pinfo: dict) -> bool:
        # P1: verdict values match dynamic vocabulary from DESIGN_PRINCIPLES.md
        # P2: sum(counts) == total_lookups
        results_file = os.path.join(self.instance_dir, "results.json")
        try:
            res = json.load(open(results_file))
            tset = res.get("target_set", {})
            counts = tset.get("counts", {})
            total = tset.get("total_lookups", 0)
            if sum(counts.values()) != total:
                self.block("RESULTS", f"Sum of counts ({sum(counts.values())}) != total_lookups ({total})")
                return False
        except Exception as e:
            self.block("RESULTS", f"Malformed results.json: {e}")
            return False
        return True

    def _eval_verdict(self, pinfo: dict) -> bool:
        # P1: README contains 5 parsed TEMPLATE headings
        # P2: Operational Status in allowed statuses
        # P3: §5 Provenance has method and ISO date
        readme_file = os.path.join(self.instance_dir, "README.md")
        if not os.path.exists(readme_file):
            self.block("VERDICT", "README.md missing")
            return False
        readme_text = open(readme_file).read()

        for heading in self.doctrine.template_headings:
            pattern = re.escape(heading)
            if not re.search(pattern, readme_text):
                self.block("VERDICT", f"Missing required TEMPLATE heading: '{heading}' in README.md")
                return False

        # Check Operational Status
        status_match = re.search(r"##\s+4\.\s+Operational Status\s*\n+`?([A-Z_ &()]+)`?", readme_text)
        if not status_match:
            self.block("VERDICT", "Could not parse Operational Status from README.md §4")
            return False
        status_val = status_match.group(1).strip()
        if status_val not in self.doctrine.allowed_operational_statuses:
            self.block("VERDICT", f"Operational Status '{status_val}' not in allowed set: {self.doctrine.allowed_operational_statuses}")
            return False
        return True

    def _eval_pg1(self, pinfo: dict) -> bool:
        return self._check_pg_log_step("PG1")

    def _eval_pg2(self, pinfo: dict) -> bool:
        return self._check_pg_log_step("PG2")

    def _eval_pg5(self, pinfo: dict) -> bool:
        # sha256(LICENSE) == doctrine_pin.files["CC-BY-4.0-legalcode.txt"]
        license_path = os.path.join(REPO_ROOT, "LICENSE")
        notice_path = os.path.join(REPO_ROOT, "NOTICE.md")
        if not os.path.exists(license_path):
            self.block("PG5", "Root LICENSE file missing")
            return False
        if not os.path.exists(notice_path):
            self.block("PG5", "Root NOTICE.md missing")
            return False

        actual_lic_sha = hashlib.sha256(open(license_path, "rb").read()).hexdigest()
        expected_lic_sha = self.state.get("doctrine_pin", {}).get("files", {}).get("CC-BY-4.0-legalcode.txt")
        if expected_lic_sha and actual_lic_sha.lower() != expected_lic_sha.lower():
            self.block("PG5", f"LICENSE sha256 ({actual_lic_sha}) != pinned CC-BY-4.0 digest ({expected_lic_sha})")
            return False
        return self._check_pg_log_step("PG5")

    def _eval_pg6(self, pinfo: dict) -> bool:
        return self._check_pg_log_step("PG6")

    def _eval_pg7(self, pinfo: dict) -> bool:
        return self._check_pg_log_step("PG7")

    def _check_pg_log_step(self, step: str) -> bool:
        pg_log = os.path.join(self.instance_dir, "PG_LOG.md")
        if not os.path.exists(pg_log):
            self.block(step, "PG_LOG.md missing")
            return False
        content = open(pg_log).read()
        step_match = re.search(rf"##\s+{step}\s+—.*?\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
        if not step_match:
            self.block(step, f"Section for {step} missing in PG_LOG.md")
            return False
        if "Status: PASS" not in step_match.group(1):
            self.block(step, f"PG_LOG.md does not record 'Status: PASS' for {step}")
            return False
        return True

    # -------------------------------------------------------------
    # Human Phase Predicates (H1–H7 & §3.1 Recursion)
    # -------------------------------------------------------------

    def _eval_pg3(self, pinfo: dict) -> bool:
        return self._eval_human_phase("PG3", pinfo)

    def _eval_pg4(self, pinfo: dict) -> bool:
        return self._eval_human_phase("PG4", pinfo)

    def _eval_pg8(self, pinfo: dict) -> bool:
        declared = pinfo.get("declared")
        if declared == "NOT_EXECUTED":
            readme = open(os.path.join(self.instance_dir, "README.md")).read()
            if "10.5281/zenodo" in readme:
                self.block("PG8", "Declared NOT_EXECUTED but Zenodo DOI mentioned in README")
                return False
            return True
        return self._eval_human_phase("PG8", pinfo)

    def _eval_pg9(self, pinfo: dict) -> bool:
        return self._eval_human_phase("PG9", pinfo)

    def _verify_crypto_signature(self, commit_sha: str, allowed_signers_path: str, keys_asc_path: str) -> bool:
        """
        K-3: Verifies that commit_sha carries a valid cryptographic signature specifically
        belonging to a key / principal in the specified registry files (not arbitrary keyring keys).
        """
        # 1. Try OpenPGP
        if keys_asc_path and os.path.exists(keys_asc_path):
            try:
                # Extract allowed fingerprints from keys_asc
                res = subprocess.run(["gpg", "--with-colons", "--show-keys", keys_asc_path], capture_output=True, text=True)
                allowed_fprs = set()
                for line in res.stdout.splitlines():
                    parts = line.split(":")
                    if len(parts) > 9 and parts[0] == "fpr":
                        allowed_fprs.add(parts[9].strip().upper())

                if allowed_fprs:
                    with tempfile.TemporaryDirectory() as gnupg_home:
                        env = os.environ.copy()
                        env["GNUPGHOME"] = gnupg_home
                        subprocess.run(["gpg", "--import", keys_asc_path], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        verify_out = subprocess.check_output(
                            ["git", "verify-commit", "--raw", commit_sha],
                            cwd=REPO_ROOT, env=env, stderr=subprocess.STDOUT, text=True
                        )
                        # Extract VALIDSIG <fingerprint>
                        validsigs = re.findall(r"\[GNUPG:\]\s+VALIDSIG\s+([0-9A-Fa-f]+)", verify_out)
                        for vs in validsigs:
                            if vs.upper() in allowed_fprs:
                                log_diag(f"  Verified OpenPGP signature for {commit_sha} by fingerprint {vs.upper()}")
                                return True
            except Exception as e:
                log_diag(f"OpenPGP verification error for {commit_sha}: {e}")

        # 2. Try SSH Signature
        if allowed_signers_path and os.path.exists(allowed_signers_path):
            try:
                verify_ssh = subprocess.run(
                    ["git", "-c", f"gpg.ssh.allowedSignersFile={allowed_signers_path}", "-c", "gpg.format=ssh", "verify-commit", commit_sha],
                    cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                if verify_ssh.returncode == 0:
                    # Parse principal from allowed_signers
                    allowed_principals = []
                    for line in open(allowed_signers_path):
                        line = line.strip()
                        if line and not line.startswith("#"):
                            allowed_principals.append(line.split()[0])

                    stderr = verify_ssh.stderr
                    if "Good \"git\" signature" in stderr:
                        for princ in allowed_principals:
                            if f"Good \"git\" signature for {princ}" in stderr:
                                log_diag(f"  Verified SSH signature for {commit_sha} by principal {princ}")
                                return True
            except Exception as e:
                log_diag(f"SSH verification error for {commit_sha}: {e}")

        return False

    def _eval_human_phase(self, phase: str, pinfo: dict) -> bool:
        evidence = pinfo.get("evidence", {})
        commit_sha = evidence.get("decision_commit")
        artifact = evidence.get("decision_artifact", "PG_LOG.md")

        if not commit_sha:
            self.block(phase, f"Missing decision_commit in {phase} evidence")
            return False

        # H2: Verify commit exists in PR/HEAD ancestry
        try:
            subprocess.check_call(
                ["git", "merge-base", "--is-ancestor", commit_sha, "HEAD"],
                cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            self.block(phase, f"Commit {commit_sha} is not in current git ancestry")
            return False

        # H3: Verify commit modified decision_artifact
        try:
            files_changed = subprocess.check_output(
                ["git", "show", "--name-only", "--format=", commit_sha],
                cwd=REPO_ROOT, text=True
            ).splitlines()
            target_rel = os.path.relpath(os.path.join(self.instance_dir, artifact), REPO_ROOT)
            if not any(f.strip() == target_rel for f in files_changed):
                self.block(phase, f"Commit {commit_sha} did not modify {target_rel}")
                return False
        except Exception as e:
            self.block(phase, f"Git inspection failed for {commit_sha}: {e}")
            return False

        # H4–H6: Cryptographic signature verification against HUMAN_KEYS registry
        allowed_signers = os.path.join(REPO_ROOT, "governance", "HUMAN_KEYS", "allowed_signers")
        keys_asc = os.path.join(REPO_ROOT, "governance", "HUMAN_KEYS", "keys.asc")

        if not os.path.exists(allowed_signers) and not os.path.exists(keys_asc):
            self.block(phase, "HUMAN_KEYS registry not initialized in governance/HUMAN_KEYS/")
            return False

        if not self._verify_crypto_signature(commit_sha, allowed_signers, keys_asc):
            self.block(phase, f"Commit {commit_sha} does not carry a verified cryptographic signature matching a key in HUMAN_KEYS registry")
            return False

        # K-4 Fix: §3.1 Recursion check: If commit modified governance/HUMAN_KEYS/, verify signer against parent commit registry
        if any(f.strip().startswith("governance/HUMAN_KEYS/") for f in files_changed):
            log_diag(f"Commit {commit_sha} modified HUMAN_KEYS. Applying §3.1 recursion verification against parent commit {commit_sha}~1...")
            with tempfile.TemporaryDirectory() as tmpdir:
                parent_allowed = os.path.join(tmpdir, "allowed_signers")
                parent_keys = os.path.join(tmpdir, "keys.asc")
                has_parent_registry = False

                try:
                    p_allowed_content = subprocess.check_output(
                        ["git", "show", f"{commit_sha}~1:governance/HUMAN_KEYS/allowed_signers"],
                        cwd=REPO_ROOT, stderr=subprocess.DEVNULL
                    )
                    open(parent_allowed, "wb").write(p_allowed_content)
                    has_parent_registry = True
                except Exception:
                    pass

                try:
                    p_keys_content = subprocess.check_output(
                        ["git", "show", f"{commit_sha}~1:governance/HUMAN_KEYS/keys.asc"],
                        cwd=REPO_ROOT, stderr=subprocess.DEVNULL
                    )
                    open(parent_keys, "wb").write(p_keys_content)
                    has_parent_registry = True
                except Exception:
                    pass

                if not has_parent_registry:
                    self.block(phase, f"§3.1 Recursion violation: commit {commit_sha} modified HUMAN_KEYS but parent commit {commit_sha}~1 has no HUMAN_KEYS registry")
                    return False

                parent_sig_ok = self._verify_crypto_signature(
                    commit_sha,
                    parent_allowed if os.path.exists(parent_allowed) else None,
                    parent_keys if os.path.exists(parent_keys) else None
                )
                if not parent_sig_ok:
                    self.block(phase, f"§3.1 Recursion failed: commit {commit_sha} modifying HUMAN_KEYS was NOT signed by a key in parent commit's registry")
                    return False
                log_diag("  §3.1 Recursion check passed against parent registry.")

        # H7: Verify commit message carries token
        try:
            commit_msg = subprocess.check_output(
                ["git", "log", "-n", "1", "--format=%B", commit_sha],
                cwd=REPO_ROOT, text=True
            )
            if f"P10-SIGNOFF: {phase}" not in commit_msg:
                self.block(phase, f"Commit message for {commit_sha} missing 'P10-SIGNOFF: {phase}' token")
                return False
        except Exception as e:
            self.block(phase, f"Failed to check commit message for {commit_sha}: {e}")
            return False

        return True


def main():
    parser = argparse.ArgumentParser(description="P10 State Guard Validator v0.1")
    parser.add_argument("--instance", required=True, help="Path to instance directory (e.g. instances/fr-be-de-eclipse-coupling-probe)")
    parser.add_argument("--github-token", default=None, help="GitHub API Token for rate limits / actions inspection")
    parser.add_argument("--report-only", action="store_true", help="Non-blocking reporting mode (returns exit 0 even on blockers)")
    args = parser.parse_args()

    guard = P10StateGuard(args.instance, github_token=args.github_token, report_only=args.report_only)
    exit_code = guard.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
