### [Link to Client Repository](https://github.com/andrewbantly/leasepeek)
### Objective
The backend of this application is engineered to efficiently process and parse data from uploaded Excel files (.xlsx), systematically save this data to a database, and expose a structured data API. It must generate and return JWTs for secured user sessions. Additionally, the backend will manage user data, incorporating password hashing and encryption, and handle user authorization and authentication processes.
### Programming language: Python

### Databases:
**MongoDB:**  Using a flexible, schema-less, JSON-style, document-based database is preferred for the property information because of the unknown nature of the excel data. Being able to create unique field and value pairs will efficiently scale and mitigate any issues of duplicate or new charge fields. 

**PostgreSQL:** Opting for a structured, schema-based, SQL-oriented database is ideal for handling user data and authentication systems due to the consistent nature of these data types. The choice of PostgreSQL, in particular, is due to its robust integration with Django, enhancing both the efficiency of our development process and the security of our application, courtesy of Django's built-in security features. 

### Framework: Django

**Rational:** Django offers a smoother experience despite its lack of native support for NoSQL databases like MongoDB. Its streamlined handling of file uploads, efficiency in creating APIs via the Django Rest Framework, and a ready-to-use admin interface outweigh this limitation. These features accelerate development and enhance application management, making Django ideal for our needs. To mitigate database compatibility issues, we're utilizing connectors to integrate MongoDB effectively, ensuring a seamless operation.