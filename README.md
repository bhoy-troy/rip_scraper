## RIP scraper
A scraper for deaths registered on [rip.ie](https://rip.ie)
    
    docker-compose up
    
    docker-compose run rip
    
    curl "https://opendata-geohive.hub.arcgis.com/datasets/d8eb52d56273413b84b0187a4e9117be_0.csv?outSR=%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D" -o data/covid.csv


## Run from the cmd line

    python -m rip.get_data -f "2017-01-01"

### Clean Up

    isort . && black .


### Git Hook

Create d pre-commit hook

    ln -s -f ./hooks/pre_commit.sh .git/hooks/pre-commit 