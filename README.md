# stocks_app - _Development Branch_

## Git Instructions

- All changes will be made here
- **DO NOT** merge to/from master, under any circumstance.
- Always work on the dev branch

```bash
git checkout -b "dev"
git fetch --all --prune
git pull origin dev --rebase # ALWAYS use the --rebase option to avoid unecessary *pull* commits
```

## Installation and Running

- To install the dependencies

```bash
mkvirtualenv stocks_app --python python3.6
pipenv install
workon stocks_app
```
- _Optionally_, you can use direnv. It loads various environemnt variables and
  (in this case) python environment(s) directly on `cd`-ing. The `.envrc` file
  has already been included. (_Mind you, you will still have to install the
  environment as stated above, but will not need to manually `workon stocks_app`
  everytime you work on the project_)

```bash
sudo apt install direnv
echo  'eval "$(direnv hook zsh)"' >> ~/.zshrc
source ~/.zshrc
cd $PROJECT_DIR
direnv allow
```
## Database

### Setup

- We will be using postgres for the database. Postgres enables a lot of
  additional fields (JSONField, HStoreField, NumericRange, etc) that make
  storage and manipulation a lot easier.
- You will have to create a postgres user called `test`, underwhich  a database
  called `stocks`, password: `test12345`.
- Keeping common credentials may involved slight more work initially, but later
  will help avoid unnecessary conflicts in the `settings.py` file.

```bash
$ sudo apt install postgres
$ sudo -u postgres -i
postgres> psql
postgres=# CREATE USER test with PASSWORD 'test12345';
postgres=# ^C
postgres> createdb stocks_app --password --owner=test
postgres> logout
```
- Once you've set this up, you should be good to go. After we begin hosting, we
  will be migrating to a centralized database with the same credentials; this
  initial setup will enable you to migrate by just changing the `HOST` in the
  database configuration.

### Migrations

- Make the initial migrations (along with the single committed one) for the
  administrative tables and postgres special field support
```
./manage.py makemigrations
./manage.py migrate
```

