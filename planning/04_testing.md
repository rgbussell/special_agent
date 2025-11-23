## unit test
* core decision-making logic for each agent should have a unit test
* tool calling should have a unit test with mock response where possible
* input/output tests for response type
* tests for updating state appropriately (database, context files)
* error handling of communication failures with APIs


## integration tests
* message exchange between agents
* coordination, deadlocks and livelocks

## system verification tests
* sub-systems will have verification tests run by github actions

## end-to-end test
* goal achievment -- has a plan be generated for example