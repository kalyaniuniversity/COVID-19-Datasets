#!/bin/bash

echo "Starting Google Sheet update service...."


cd $PWD/tools/Automator;

python main.py;

if [ $? -eq 0 ]; then
    echo "removing old sheet from disk..."

    rm ../../India\ Statewise\ Confirmed\ Cases/COVID19_INDIA_STATEWISE_TIME_SERIES_CONFIRMED.csv
    rm ../../India\ Statewise\ Recovery\ Cases/COVID19_INDIA_STATEWISE_TIME_SERIES_RECOVERY.csv
    rm ../../India\ Statewise\ Death\ Cases/COVID19_INDIA_STATEWISE_TIME_SERIES_DEATH.csv

    echo "...done!"
    echo "moving new sheet to their actual place..."

    mv COVID19_INDIA_STATEWISE_TIME_SERIES_CONFIRMED.csv ../../India\ Statewise\ Confirmed\ Cases/
    mv COVID19_INDIA_STATEWISE_TIME_SERIES_RECOVERY.csv ../../India\ Statewise\ Recovery\ Cases/
    mv COVID19_INDIA_STATEWISE_TIME_SERIES_DEATH.csv ../../India\ Statewise\ Death\ Cases/

    echo "...done!"
    echo "pushing to git..."

    cd ../../
    
    
    git config --global user.email "$EMAIL_ID"
    git config --global user.name "$USER_NAME"
    git status
    git add .
    git commit -m "datasets updated by automator"
    
    git push origin master

    echo "...done!"

else
    echo "Sheet update Failure"
    echo "Nothing to push"
fi
