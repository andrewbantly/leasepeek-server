### Objective
The backend of this application should be able to handle excel files (such as .xlsx), parse the data, save the data to a database, produce an API with the structured data, and return that API endpoint. It should also store user information, password hashing/encryption, and handle authorization and authentication. 
### Programming language: Python

## Database
**Decision:** MongoDB

**Rational:** Using a flexible, schema-less, JSON-style, document-based database is preferred because of the unknown nature of the excel data. Being able to create unique field and value pairs will efficiently scale and mitigate any issues of duplicate or new charge fields. 

## Framework
**Candidates:**
- Django
- Flask
- FastAPI

**Decision:** Django

**Potential Challenges:** Django doesn't natively support NoSQL databases like MongoDB. 

**Rational:** Django offers a smoother experience when it comes to handling file uploads, creating APIs (especially with Django Rest Framework), and providing an admin interface. 