## RIP scraper
A scraper for deaths registered on [rip.ie](https://rip.ie)

    mkdir data && curl "https://opendata-geohive.hub.arcgis.com/datasets/d8eb52d56273413b84b0187a4e9117be_0.csv" -o data/covid.csv
    
    docker-compose up

Or alternativelty get the data first by 
    docker-compose run rip


## Run from the cmd line

    python -m rip.get_data -f "2017-01-01"

### Clean Up

    isort . && black .


### Git Hook

Create d pre-commit hook

    ln -s -f ./hooks/pre_commit.sh .git/hooks/pre-commit 
    
### Docker Linting

    docker run --rm -i hadolint/hadolint < images/rstudio/Dockerfile
    docker run --rm -i hadolint/hadolint < images/python_rip/Dockerfile