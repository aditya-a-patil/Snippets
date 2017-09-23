#!/usr/bin/env bash

# tls_ciphers.sh is a simple script to test SSL/TLS protocols supported by servers.
# This script uses openssl to make connections to the host provided.
# Usage: $ ./tls_ciphers.sh -u <HOST> [-p <port>] [-o < all | tls1_2 | tls1_1 | tls1 | ssl3 | dtls1 >]
# Only 'host' is a required paramter.
# If no port is provided then the script assumes 443 by default.
# Also, if no option for protocol is provided then all available protocols are tested.

# As of now either all protocols can be tested together or individually.
# Future update will have capability to test multiple protocols same time.

set -o errexit

# Set delay between each request sent. Lower than 0.3sec may cause certain websites to reject connections.
DELAY=0.3

declare -a protocol_list=("tls1_2" "tls1_1" "tls1" "ssl3" "dtls1")

usage() { echo "Usage: $0 -u <HOST> [-p <port>] [-o < all | tls1_2 | tls1_1 | tls1 | ssl3 | dtls1 >]" 1>&2; exit 1; }

# extract options and their arguments into variables.
while getopts ":u:p:o:" o; do
    case "${o}" in
        u)
            URL=${OPTARG}
            ;;
        p)
            PORT=${OPTARG}
            ;;
        o)
			PROTOCOL=${OPTARG}
			;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

# sanity check URL is compulsorily provided
if [ -z "${URL}" ]; then
    usage
fi

# if port is not specified then default it to 443
if [[ -z "${PORT}" ]]; then
	PORT=443
fi

# if protocol is not specified then default it to test all
if [[ -z "${PROTOCOL}" ]]; then
	PROTOCOL=all
fi

# sanity check if protocol provided is valid
if [[ "${PROTOCOL}" != "all" ]]; then
	valid_protocol=false
	for item in "${protocol_list[@]}"; do
	    [[ ${PROTOCOL} == "${item}" ]] && valid_protocol=true
	done
	if [[ "$valid_protocol" = false ]]; then
		echo "${PROTOCOL} not a supported/valid protocol"
		exit 1;
	fi
fi

echo -ne "Obtaining cipher list from $(openssl version)."
{
    ciphers=$(openssl ciphers 'ALL:eNULL' | sed -e 's/:/ /g') &&
    echo " ...[OK]"
} || {
	echo " ...[ERR]"
}

echo -ne "Connecting to ${URL}:${PORT}  "
ping -c 1 ${URL} > /dev/null
if [[ $? = 0 ]]; then
	echo "...[OK]"
else
	echo " ...[ERR]"
	echo "Could not connect to target."
fi

test_protocol() {
	current_protocol=$1
	echo -e "\nTesting ciphers supported with $current_protocol:"
	cipher_supported=false
	for cipher in ${ciphers[@]}
	do
		result=$(echo -n | openssl s_client -cipher "$cipher" -$current_protocol -connect ${URL}:${PORT} 2>&1) || true
		if [[ "${result}" =~ ":error:" ]]
		then
		  error=$(echo -n ${result} | cut -d':' -f6)
		  #echo NO \($error\)
		else
			cipher_supported=true
			if [[ "${result}" =~ "Cipher is ${cipher}" || "${result}" =~ "Cipher    :" ]] ; then
				echo $cipher
			else
				echo UNKNOWN RESPONSE
				echo ${result}
			fi
		fi
		sleep ${DELAY}
	done
	if [ "${cipher_supported}" = false ]
	then
		echo No Ciphers supported
	fi;
}

if [[ "${PROTOCOL}" = "all" ]]; then
	for i in "${protocol_list[@]}"
	do 
   		test_protocol ${i}
	done
else
	test_protocol ${PROTOCOL}
fi