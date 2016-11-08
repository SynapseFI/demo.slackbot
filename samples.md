## Slackbot commands
Enter these commands in Slack when @synapse is in the channel.

#### Help
```
@synapse help
```

#### Register new user
```
@synapse register name Steven Broderick | email steven@synapsepay.com | phone 555-555-5555
```

#### See your user info
```
@synapse whoami
```

#### Add address
```
@synapse add_address street 742 Evergreen Terrace | city Springfield | state OR | zip 94110 | dob 3/19/1942
```

#### Add SSN
```
@synapse add_ssn 2222
```

#### Add photo ID
```
# as the comment text for the image
@synapse add_photo_id
```

#### Add node
```
@synapse add_node nickname Primary Checking | account 112222555 | routing 051000017 | type CHECKING
@synapse add_node nickname Rainy Day Fund | account 2222222222 | routing 051000017 | type SAVINGS
```

#### Verify a node's microdeposits
```
@synapse verify NODE_ID 0.1 0.1
```

#### List nodes
```
@synapse list_nodes
```

#### List transactions
```
@synapse list_transactions from FROM_NODE_ID
```

#### Send a transaction
```
@synapse send 1.00 from SENDING_NODE_ID to RECEIVING_NODE_ID
```

#### Schedule a transaction (in days only)
```
@synapse send 1.00 from SENDING_NODE_ID to RECEIVING_NODE_ID in 2 days
```

#### Set up a recurring transaction (in days only)
```
@synapse send 1.00 from SENDING_NODE_ID to RECEIVING_NODE_ID every 30 days
```
