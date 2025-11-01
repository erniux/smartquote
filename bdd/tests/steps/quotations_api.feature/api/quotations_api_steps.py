# -*- coding: utf-8 -*-
# Auto-generated from behave --dry-run snippets
from behave import given, when, then

@given(u'the user is authenticated as a manager or admin')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'Given the user is authenticated as a manager or admin')


@when(u'the user sends a GET request to \'/api/quotations/\'')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'When the user sends a GET request to \'/api/quotations/\'')


@then(u'the system should return a list of quotations')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'Then the system should return a list of quotations')


@then(u'the list should include at least:')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'Then the list should include at least:')


@given(u'the user is authenticated as an admin or manager')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'Given the user is authenticated as an admin or manager')


@given(u'there are no active quotations')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'Given there are no active quotations')


@when(u'the user sends a POST request to \'/api/quotations/\' with the following data:')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'When the user sends a POST request to \'/api/quotations/\' with the following data:')


@then(u'the system should create a new quotation with the provided data')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'Then the system should create a new quotation with the provided data')


@then(u'the created quotation should be included in the list of quotations returned by the GET request to \'/api/quotations/\'')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'Then the created quotation should be included in the list of quotations returned by the GET request to \'/api/quotations/\'')


@when(u'the user sends a POST request to \'/api/quotations/{quote_id}/duplicate\' with query parameters: `status=draft`')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'When the user sends a POST request to \'/api/quotations/{quote_id}/duplicate\' with query parameters: `status=draft`')


@then(u'the system should create a new quotation that is a duplicate of the specified one')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'Then the system should create a new quotation that is a duplicate of the specified one')


@then(u'the newly created quotation should have the same properties as the original one, except for the id and created/modified timestamps')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'Then the newly created quotation should have the same properties as the original one, except for the id and created/modified timestamps')


@then(u'the status of the newly created quotation should be \'draft\'')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'Then the status of the newly created quotation should be \'draft\'')


@when(u'the user sends a PUT request to \'/api/quotations/{quote_id}/cancel\'')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'When the user sends a PUT request to \'/api/quotations/{quote_id}/cancel\'')


@then(u'the system should cancel the specified quotation')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'Then the system should cancel the specified quotation')


@then(u'the status of the cancelled quotation should be \'cancelled\'')
def step_impl(context):
    pass
    raise StepNotImplementedError(u'Then the status of the cancelled quotation should be \'cancelled\'')
