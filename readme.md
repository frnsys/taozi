User management is handled via the `flask` management program.

## Setup

## Usage

To create the admin role:

    flask roles create admin

To create a user and make them an admin:

    flask users create <EMAIL>
    flask users activate <EMAIL>
    flask roles add <EMAIL> admin

The login at `/login` and access the admin backend at `/admin`.

![](shot.png)

## Demo

To run a demo application: `python app.py`
