# web_backend


### Week 3 Todo
1. Create MongoDB Atlas Cluster and Sync dbname, collection name and datarep
2. Try to Modularize (merging files) as much as possible and create a main `app.py` file
3. Testing APIs / Completing All APIs

### Week 4 Todo
- [ ] Create a file MongoConnection.py, which has a connecter class and functions that CRUDs data from the database, similar to `newformat/modules/beta.py`

- [X] Choose either Blueprint or newformat 
- [X] MongoDB should be a ENVVAR
- [X] Better naming instead of contributer initials
- [X] Overall API Testing
- [X] Fill up database with some sample data

Fun Challenge:
- [X] Create rules to the branch such that no one can push to the main branch directly and if someone should make changes to the main branch they should make a pr from elsewhere and the PR should def be approved by `n` number of reviewers.
- [ ] Try API testing with Github Actions, i.e., whenever someone makes a PR, it should check the APIs and see if it gives the expected output for sample input
