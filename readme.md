User management is handled via the `flask` management program.

To create the admin role:

    flask roles create admin

To create a user and make them an admin:

    flask users create <EMAIL>
    flask users activate <EMAIL>
    flask roles add <EMAIL> admin

The login at `/login`.

![](shot.png)
