ansible-galaxy collection install -p ./collections https://github.com/tryfan/ansible-collection-morpheus-core/releases/download/v0.2.2/morpheus-core-0.2.2.tar.gz
sed -i -r "s@MORPHEUSURL@$morpheus_url@" group_vars/all
sed -i -r "s@AWSACCESSKEY@$AWS_ACCESS_KEY_ID@" group_vars/all
sed -i -r "s@AWSSECRETKEY@$AWS_SECRET_ACCESS_KEY@" group_vars/all
echo morpheus_token: $(curl -XPOST "${morpheus_url}/oauth/token?grant_type=password&scope=write&client_id=morph-api" --data-urlencode 'username=admin' --data-urlencode 'password=morphPass1@' | jq -r '.access_token') >> group_vars/all
echo ansible_test_version: $ANSIBLE_VERSION >> group_vars/all
