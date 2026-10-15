"""Regression checks for release validation, without model calls or real text."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_shortcuts import ACTION_PREFIX, english_helper
from validate_sources import validate_workflow


class WorkflowValidationTests(unittest.TestCase):
    def setUp(self):
        self.workflow = copy.deepcopy(english_helper())
        self.actions = self.workflow['WFWorkflowActions']

    def find(self, name):
        return next(a for a in self.actions if a['WFWorkflowActionIdentifier'] == ACTION_PREFIX + name)

    def check_rejected(self, message):
        with self.assertRaisesRegex(ValueError, message):
            validate_workflow(self.workflow, product=True)

    def test_current_workflow_is_valid(self):
        validate_workflow(self.workflow, product=True)

    def test_cloud_model_is_rejected(self):
        self.find('askllm')['WFWorkflowActionParameters']['WFLLMModel'] = 'Apple Intelligence'
        self.check_rejected('on-device')

    def test_removing_copy_confirmation_is_rejected(self):
        index = next(i for i, a in enumerate(self.actions)
                     if a['WFWorkflowActionIdentifier'] == ACTION_PREFIX + 'setclipboard')
        self.actions[index - 1]['WFWorkflowActionParameters']['WFAlertActionCancelButtonShown'] = False
        self.check_rejected('cancellable preview')

    def test_copying_wrong_output_is_rejected(self):
        model = self.find('askllm')['WFWorkflowActionParameters']['UUID']
        self.find('setclipboard')['WFWorkflowActionParameters']['WFInput']['Value']['OutputUUID'] = model
        self.check_rejected('actual replacement')

    def test_unknown_output_reference_is_rejected(self):
        self.find('setclipboard')['WFWorkflowActionParameters']['WFInput']['Value']['OutputUUID'] = 'missing'
        self.check_rejected('unknown/forward')

    def test_mismatched_group_is_rejected(self):
        self.find('conditional')['WFWorkflowActionParameters']['GroupingIdentifier'] = 'different'
        self.check_rejected('control flow group')

    def test_bad_utf16_attachment_range_is_rejected(self):
        text = self.find('gettext')['WFWorkflowActionParameters']['WFTextActionText']['Value']
        text['attachmentsByRange'] = {'{1, 1}': next(iter(text['attachmentsByRange'].values()))}
        self.check_rejected('UTF-16')

    def test_added_network_action_is_rejected(self):
        self.actions.insert(1, {'WFWorkflowActionIdentifier': ACTION_PREFIX + 'downloadurl',
                                'WFWorkflowActionParameters': {}})
        self.check_rejected('unexpected action')


if __name__ == '__main__':
    unittest.main()
