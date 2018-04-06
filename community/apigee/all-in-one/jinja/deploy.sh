gcloud deployment-manager deployments create $1 --config apigee-edge.yaml
red=`tput setaf 1`
green=`tput setaf 2`
blue=`tput setaf 4`
reset=`tput sgr0`
zone=$(cat apigee-edge.yaml | grep zone)
zone=$(echo $zone | cut -d':' -f2 | sed -e 's/^[ \t]*//')
natIP=$(gcloud compute instances describe $1 --zone $zone --format yaml | grep natIP)
IP=$(echo $natIP | grep -oE "[^:]+$")
IP="${IP#"${IP%%[![:space:]]*}"}"   # remove leading whitespace characters
IP="${IP%"${IP##*[![:space:]]}"}"
admin_email=$(echo $(cat aio-config.txt | grep ADMIN_EMAIL) | cut -d'=' -f2 | sed -e 's/^[ \t]*//' | cut -d' ' -f1 )
admin_password=$(echo $(cat aio-config.txt | grep APIGEE_ADMINPW) | cut -d'=' -f2 | sed -e 's/^[ \t]*//' | cut -d' ' -f1 )
dp_admin_email=$(echo $(cat dp-config.txt | grep DEVPORTAL_ADMIN_EMAIL) | cut -d'=' -f2 | sed -e 's/^[ \t]*//' | cut -d' ' -f1 )
dp_admin_password=$(echo $(cat dp-config.txt | grep DEVPORTAL_ADMIN_PWD) | cut -d'=' -f2 | sed -e 's/^[ \t]*//' | cut -d' ' -f1 )
echo "${red}Please allow 15 minutes for edge to be installed";
echo "${blue}Please access the management UI at ${green}http://$IP:9000";
echo "${blue}Management Server is at ${green}http://$IP:8080";
echo "${blue}Cred to access EdgeUI/Managament Server is :"${green}$admin_email/$admin_password
echo "${blue}The API endpoint runs at ${green}http://$IP:9001";
echo "${blue}Please access the Devportal UI at ${green}http://$IP:8079";
echo "${blue}Cred to Login devportal  is :"${green}$dp_admin_email/$dp_admin_password

echo "${blue}Please access the Monitoring Dashboard UI at ${green}http://$IP:3000";
echo "${blue}Creds for Monitoring Dashboard ${green}admin/admin${reset}";
