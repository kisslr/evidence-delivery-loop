import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "skills/evidence-delivery-loop/SKILL.md").read_text(encoding="utf-8")
SAFETY = (ROOT / "skills/evidence-delivery-loop/references/safety-matrix.md").read_text(encoding="utf-8")
ROUTING = (ROOT / "skills/evidence-delivery-loop/references/format-routing.md").read_text(encoding="utf-8")
OUTPUT = (ROOT / "skills/evidence-delivery-loop/references/output-contract.md").read_text(encoding="utf-8")


class UntrustedDataPostureTests(unittest.TestCase):
    def test_inputs_treated_as_untrusted_data(self):
        self.assertIn("untrusted data", SKILL)

    def test_system_rules_are_only_authority(self):
        self.assertIn("system rules", SKILL)
        self.assertIn("explicit user authorization", SKILL)

    def test_plan_files_do_not_grant_authorization(self):
        self.assertIn("plan file is data, not authorization", SKILL)

    def test_material_content_never_grants_authorization(self):
        self.assertIn("never grant authorization", SAFETY)


class FabricationAndProvenanceTests(unittest.TestCase):
    def test_no_fabrication_without_materials(self):
        self.assertIn("Do not fabricate findings", SKILL)

    def test_no_ai_detection_score_claim(self):
        self.assertIn("AI-detection score", SKILL)

    def test_no_author_impersonation(self):
        self.assertIn("impersonate an author", SKILL)

    def test_no_conceal_provenance(self):
        import re
        self.assertTrue(
            re.search(r"conceal\s+provenance", SKILL),
            "SKILL.md must prohibit concealing provenance",
        )

    def test_originals_preserved_by_default(self):
        self.assertIn("unchanged by default", SKILL)


class PathAndNetworkSafetyTests(unittest.TestCase):
    def test_symlink_and_junction_must_be_blocked(self):
        self.assertIn("symlink", SAFETY)
        self.assertIn("junction", SAFETY)

    def test_path_canonicalization_required(self):
        self.assertIn("Canonicalize", SAFETY)
        self.assertIn("canonicalize", SKILL.lower())

    def test_ssrf_loopback_protection(self):
        self.assertIn("loopback", SAFETY)

    def test_ssrf_private_network_protection(self):
        self.assertIn("private", SAFETY)

    def test_ssrf_link_local_protection(self):
        self.assertIn("link-local", SAFETY)

    def test_ssrf_metadata_address_protection(self):
        self.assertIn("metadata", SAFETY)

    def test_dangerous_protocol_rejection(self):
        lower_safety = SAFETY.lower()
        has_protocol_rule = "http" in lower_safety or "protocol" in lower_safety
        self.assertTrue(has_protocol_rule, "safety-matrix must address protocol restrictions")

    def test_scan_bounds_are_documented(self):
        self.assertIn("depth", SAFETY)
        self.assertIn("count", SAFETY)
        self.assertIn("size", SAFETY)


class PermissionBoundaryTests(unittest.TestCase):
    def test_all_five_safety_levels_present(self):
        for level in ("S0", "S1", "S2", "S3", "S4"):
            self.assertIn(level, SKILL, f"{level} missing from SKILL.md")
            self.assertIn(level, SAFETY, f"{level} missing from safety-matrix.md")

    def test_s0_is_read_only_default(self):
        self.assertIn("read-only", SKILL)
        self.assertIn("Default to S0", SKILL)

    def test_s4_blocked_by_default(self):
        self.assertIn("blocked by default", SAFETY)
        self.assertIn("S4", SAFETY)

    def test_s3_requires_separate_confirmation(self):
        self.assertIn("separate confirmation", SAFETY)

    def test_s2_requires_explicit_confirmation(self):
        self.assertIn("explicit confirmation", SAFETY)

    def test_authorization_is_operation_specific(self):
        self.assertIn("specific to the named operation", SAFETY)


class FormatRoutingTests(unittest.TestCase):
    def test_all_format_types_routed(self):
        for fmt in ("Markdown", "JSON", "YAML", "CSV", "DOCX", "PDF", "PPTX", "XLSX", "IPYNB"):
            self.assertIn(fmt, ROUTING, f"{fmt} missing from format-routing.md")

    def test_capability_gap_fallback_exists(self):
        self.assertIn("capability_gap", ROUTING)

    def test_public_url_routing(self):
        self.assertIn("Public URL", ROUTING)

    def test_login_gated_url_routing(self):
        self.assertIn("Login-gated", ROUTING)

    def test_no_infer_rendering_from_presence(self):
        self.assertIn("Do not infer", ROUTING)


class WorkflowConstraintTests(unittest.TestCase):
    def test_only_one_second_cycle(self):
        self.assertIn("one second cycle", SKILL)

    def test_audit_retrospective_exists(self):
        self.assertIn("Audit retrospective and root cause", SKILL)

    def test_solution_plan_review_before_execution(self):
        self.assertIn("Solution plan and plan review", SKILL)

    def test_verify_independent_of_generation(self):
        self.assertIn("independently", SKILL)

    def test_evaluation_uses_relative_grades(self):
        for grade in ("pass", "partial", "fail", "unknown"):
            self.assertIn(grade, OUTPUT)

    def test_no_numeric_certainty(self):
        self.assertIn("numeric certainty", OUTPUT)


class InjectionResistanceTests(unittest.TestCase):
    def test_prompt_injection_fixture_is_labeled_as_data(self):
        fixture = (ROOT / "examples/prompt-injection-material.txt").read_text(encoding="utf-8")
        self.assertIn("not instructions for the agent", fixture)

    def test_input_controls_exclude_secrets(self):
        self.assertIn("credential", SAFETY.lower())

    def test_browser_session_requires_authorization(self):
        self.assertIn("authorized browser session", SKILL)

    def test_no_credential_extraction(self):
        self.assertIn("do not extract passwords", SKILL)


class AbortAndRecoveryTests(unittest.TestCase):
    def test_abort_conditions_are_documented(self):
        self.assertIn("aborted", SKILL)
        self.assertIn("Stop the loop early", SKILL)

    def test_partial_material_handling(self):
        self.assertIn("blocked", SKILL)
        self.assertIn("missing", SKILL.lower())

    def test_scope_change_does_not_restart(self):
        self.assertIn("Do not silently restart", SKILL)

    def test_processor_error_recovery(self):
        self.assertIn("fails at runtime", ROUTING)
        self.assertIn("does not abort", ROUTING)


class ExtendedFormatRoutingTests(unittest.TestCase):
    def test_archive_formats_routed(self):
        for fmt in ("ZIP", "TAR", "RAR", "7z"):
            self.assertIn(fmt, ROUTING, f"{fmt} missing from routing table")

    def test_image_formats_routed(self):
        for fmt in ("PNG", "JPG", "SVG"):
            self.assertIn(fmt, ROUTING, f"{fmt} missing from routing table")

    def test_audio_video_out_of_scope(self):
        self.assertIn("out of scope", ROUTING.lower())

    def test_email_formats_routed(self):
        self.assertIn("MSG", ROUTING)
        self.assertIn("EML", ROUTING)


class OutputScalingTests(unittest.TestCase):
    def test_output_scales_with_material_count(self):
        self.assertIn("Scale response detail", OUTPUT)

    def test_large_sets_use_file_output(self):
        import re
        self.assertTrue(
            re.search(r"complete\s+report\s+in\s+a\s+file", OUTPUT),
            "output-contract must direct large reports to a file",
        )


class MultiLanguageTests(unittest.TestCase):
    def test_output_language_follows_request(self):
        self.assertIn("output language", SKILL.lower())

    def test_mixed_language_quoting(self):
        self.assertIn("original language", SKILL)


if __name__ == "__main__":
    unittest.main()
