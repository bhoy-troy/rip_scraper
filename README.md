## RIP scraper
A scraper for deaths registered on [rip.ie](https://rip.ie)
    
    docker-compose up
    
    docker-compose run rip

## Run from the cmd line

    python -m rip.get_data -f "2017-01-01"

### Clean Up

    isort . && black .
