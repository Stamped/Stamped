#!/bin/bash -ex

# TODO: make this script idempotent!

echo '>>>> Create keys for root to connect to GitHub'
echo "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAvAzcTXbF0V/Pjja3b2Q9hsBQSHv8R8S6yoESb6CuR5HNzD3rIcfP9r2t3dJnVjeCZKx4JTadGXAr7ysVysGMLgbUMkngJ0bgnqkXPfLnKW07uYsrAF6Q1Gz79RSEIFfQP53p8XKpIkiRnbogM5RG2aIjJobuAsu0J8F9bGL6UfoRv1gGR0VcDbWAnp5SV8iJUBI0ULvVmdKKkFyeVHEZe2zjoplFr4b9jAUwDnNYpWobmsNoC4+1pw5fZRREJ32gCp4iYJIN5eJvylfpbhp6DtKPqrWmCEtIeVkS9pvqgVrlXMiaOPG972FuQJWiC5/iMApUlcTwCcAWkWfRTC4K1w== devbot@stamped.com" > ~/.ssh/id_rsa.pub
echo "-----BEGIN RSA PRIVATE KEY-----" > ~/.ssh/id_rsa
echo "MIIEogIBAAKCAQEAvAzcTXbF0V/Pjja3b2Q9hsBQSHv8R8S6yoESb6CuR5HNzD3r" >> ~/.ssh/id_rsa
echo "IcfP9r2t3dJnVjeCZKx4JTadGXAr7ysVysGMLgbUMkngJ0bgnqkXPfLnKW07uYsr" >> ~/.ssh/id_rsa
echo "AF6Q1Gz79RSEIFfQP53p8XKpIkiRnbogM5RG2aIjJobuAsu0J8F9bGL6UfoRv1gG" >> ~/.ssh/id_rsa
echo "R0VcDbWAnp5SV8iJUBI0ULvVmdKKkFyeVHEZe2zjoplFr4b9jAUwDnNYpWobmsNo" >> ~/.ssh/id_rsa
echo "C4+1pw5fZRREJ32gCp4iYJIN5eJvylfpbhp6DtKPqrWmCEtIeVkS9pvqgVrlXMia" >> ~/.ssh/id_rsa
echo "OPG972FuQJWiC5/iMApUlcTwCcAWkWfRTC4K1wIBIwKCAQAVfdAI2l/AKDT6T2Vr" >> ~/.ssh/id_rsa
echo "0PEWtuSakdOwbkE7tvrK7crGWc5gfBrfSgkjg2RT3YgnHElql14wI3+rIsMxRsCp" >> ~/.ssh/id_rsa
echo "dTSXi8B6xp1GUT4+BLIy9zBcgYMrJdkHW0PAgXvhfrADskOvf8L3Bcovzcd/vYAF" >> ~/.ssh/id_rsa
echo "5Q9pVFvJ44jqYGxcUKCerDnde3fmxRqmZT96NnY2VQcDXJWOs4Z0n5cN5caobZ4Q" >> ~/.ssh/id_rsa
echo "rFnOa23YbY0EFsUrrl1cFsfxy0LhXWJFIS38SaIQ2RNIxMVgOGvelN6aah1hROn2" >> ~/.ssh/id_rsa
echo "sYRbiYXpGEIGU6xsOtBY79SAX4NYIhFfJuCACQyQp8Iq+QXolggl0NkK0jY2blNt" >> ~/.ssh/id_rsa
echo "MiirAoGBAPAjjWUlJVTvRoVIygiWEVNW2uJOjl2MfkO/LgYOzlczpz87QRMEfeBD" >> ~/.ssh/id_rsa
echo "jz6CyqNCsiJZwW/1tdcjwkpBNPuVIHFHjPTv0VBZ852YTy0Z5vga681VRbNiDP7T" >> ~/.ssh/id_rsa
echo "Jkltgoft8S4fBYZ/WvFaqhq1Mk/k5hMVLEd8mnVEzCG5NWUTN0gzAoGBAMh4jffy" >> ~/.ssh/id_rsa
echo "KhuxEnD6bExkTRlYlHmFuQ5TubyPb3EzvrB5maNBmaDHQeAKQECl4V/fBXANENw4" >> ~/.ssh/id_rsa
echo "94wjx8sQc9/Vo2+5I32VKiHEzlEe7b0lojvS826d27Du4iTzMCp+5t8wJfn6mPu5" >> ~/.ssh/id_rsa
echo "AqA0aCWZp28utttnvUXORw+mRJp77RI9f97NAoGAUlVVDLxHUFIJjMh/yG33T8YB" >> ~/.ssh/id_rsa
echo "5zDgWpaRsNPVQ+fRt39sirU64fLpVDRroGdbayzPXDwHzp1i6q0sq76V0pmHd0u7" >> ~/.ssh/id_rsa
echo "TKn+nzTIjc3SANWuRm+hTbbWEZ3107YbwWdf9BcQ3Jzr85lhAkr4fi9+9tIi/zp1" >> ~/.ssh/id_rsa
echo "lNpDleuzs8p4tPClPVMCgYEAg7zvlE6t9PC0WN8T96+gYRzz2tQ3x5Ya+EEAFzCh" >> ~/.ssh/id_rsa
echo "4a7+j9qmyL10bqemkOIJIb5xSaIvpqkXs9z/orMKUUM/g+6w7CAxoSmO5NnPbasE" >> ~/.ssh/id_rsa
echo "NfEGXqI/6UyF+wY1mETDmfsRpEWXu1xSLsNaYdoAUGCGyrHix3js3mXykWdhRoAv" >> ~/.ssh/id_rsa
echo "dScCgYEAxOhXQNfCBQPBiVaApYCblNb0ASMh9gQyh5ZVhdcGu84qpTTxt2cIOV2p" >> ~/.ssh/id_rsa
echo "ylKJVSS3R3bzPw3goGkvFL0e7Mlzr7uwj70pGqw1kXzbe4pLC1GE3PC4QlvPA8lE" >> ~/.ssh/id_rsa
echo "WCy7/RohwIRd02/7s7UUW118xQYcrT27o/4BJpNd1uWsUT07BgI=" >> ~/.ssh/id_rsa
echo "-----END RSA PRIVATE KEY-----" >> ~/.ssh/id_rsa
echo "" >> ~/.ssh/id_rsa

echo '>>>> Set permissions for keys'
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub

echo '>>>> Install git'
while :; do
    if apt-get -y install git-core; then
        break
    else
        sleep 1
    fi
done

echo '>>>> Set bash to ignore errors, then run ssh so that clone command ignores validation of URL'
set +e
ssh -o StrictHostKeyChecking=no git@github.com
set -e

echo '>>>> Clone repo'

if [ ! -d /stamped ]; then
    mkdir -p /stamped
    
    while :; do
        if [ ! -d /stamped/bootstrap ]; then
            set +e
            git clone git@github.com:Stamped/stamped-bootstrap.git /stamped/bootstrap
            set -e
        else
            break
        fi
    done
fi

cd /stamped/bootstrap
git pull

echo '>>>> Installing python-setuptools'
while :; do
    if apt-get -y install python-setuptools; then
        break
    else
        sleep 1
    fi
done

echo '>>>> Running init script'
python /stamped/bootstrap/init.py '{{ init_params }}' >& /stamped/bootstrap/log &

