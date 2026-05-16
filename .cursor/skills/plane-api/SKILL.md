---
name: plane-api
description: Overview of Plane's API Docucmentation. The Plane API is organized around REST. Our API has predictable resource-oriented URLs, accepts application/json request bodies, returns JSON responses, and uses standard HTTP response codes, authentication, and verbs.
---

Base URL [​](#base-url)
-----------------------

All requests to the Plane Cloud API must be made to the following base URL:

This URL should be prefixed to all endpoint paths.

For example, to retrieve all projects in a workspace:

```
GET https://api.plane.so/api/v1/workspaces/{workspace_slug}/projects/
```


TIP

If you're using a self-hosted instance of Plane, your API base URL will differ based on your custom domain and setup.

Authentication [​](#authentication)
-----------------------------------

Our APIs use a key for authentication. The API key should be included in the header of each request to verify the client's identity and permissions. The key should be passed as the value of the `X-API-Key` header.

INFO

You must have a Plane account or be registered to your instance to generate a key.

### Generating an API Key [​](#generating-an-api-key)

1.  Log into your Plane account and go to **Profile Settings**.
2.  Go to **Personal Access Tokens** in the list of tabs available.
3.  Click `Add personal access token`.
4.  Choose a title and description so you know why you are creating this token and where you will use it.
5.  Choose an expiry if you want this to stop working after a point.

### Using the API Key [​](#using-the-api-key)

To authenticate an API request, include your API key in the request header:

```
X-API-Key: <Your-API-Key>
```


It is important to keep your API key confidential to prevent unauthorized access to your account.

### Using an OAuth Token [​](#using-an-oauth-token)

If your application uses [OAuth](https://developers.plane.so/dev-tools/build-plane-app/overview) to obtain user authorization (for example, a Plane app you've built), you can authenticate API requests with the OAuth access token. Include the token in the `Authorization` header as a Bearer token:

```
Authorization: Bearer <your-oauth-access-token>
```


The access token is scoped to the permissions (scopes) the user granted when authorizing your app. See [OAuth scopes](https://developers.plane.so/dev-tools/build-plane-app/oauth-scopes) for the full list of available scopes.

### Example of an Authenticated API Request [​](#example-of-an-authenticated-api-request)

**Using an API key:**

```
GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/
Headers:
  X-API-Key: plane_api_<token>
```


**Using an OAuth token:**

```
GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/
Headers:
  Authorization: Bearer <your-oauth-access-token>
```


**Response:**

### Error Handling [​](#error-handling)

*   **Missing API Key**: If the `X-API-Key` header is not included, the API will return an error indicating that authentication is required.
*   **Invalid API Key**: If the provided API key is invalid or expired, the API will return an error message indicating an authentication failure.

### Security Recommendations [​](#security-recommendations)

*   **Keep the API Key Secret**: Treat your API key like a password. Do not share it or expose it in client-side code.
*   **Regenerate Key If Compromised**: If you suspect that your API key has been compromised, generate a new one immediately and update your applications.

* * *

HTTP Methods [​](#http-methods)
-------------------------------

HTTP defines a set of request methods, also known as HTTP verbs, to indicate the desired action for a given resource.


|Verb  |Description                                        |Example                        |
|------|---------------------------------------------------|-------------------------------|
|GET   |Requests a representation of the specified resource|Fetch all issues from a project|
|POST  |Submits an entity to the specified resource        |Create a project               |
|DELETE|Deletes the specified resource                     |Delete a module-issue          |
|PATCH |Applies partial modifications to a resource        |Edit a module                  |


Status Codes [​](#status-codes)
-------------------------------

### Success Responses [​](#success-responses)



* Status Code: 200 OK
  * Description: The request succeeded, and a new resource was created, generally sent in GET or PATCH requests.
* Status Code: 201 Created
  * Description: The request is succeeded, and a new resource was created, generally sent in POST or PATCH requests.
* Status Code: 204 No Content
  * Description: The request is succeeded, and no body is sent, generally comes from the DELETE request.


### Error Responses [​](#error-responses)



* Status Code: 400 Bad Request
  * Description: The server cannot or will not process the request due to something that is perceived to be a client error.
* Status Code: 401 Unauthorized
  * Description: Although the HTTP standard specifies "unauthorized", semantically, this response means "unauthenticated". That is, the client must authenticate itself to get the requested response.
* Status Code: 404 Not Found
  * Description: The server cannot find the requested resource. This means the URL is not recognized.
* Status Code: 429 Throttling Error
  * Description: The server is processing too many requests at once and is unable to process your request. Retry the request after some time.
* Status Code: 500 Internal Server Error
  * Description: The server has encountered a situation it does not know how to handle.
* Status Code: 502 Bad Gateway
  * Description: This error response means that the server got an invalid response while working as a gateway to get a response needed to handle the request.
* Status Code: 503 Service Unavailable
  * Description: The server is not ready to handle the request. Common causes are a server that is down for maintenance or is overloaded.
* Status Code: 504 Gateway Timeout
  * Description: This error response is given when the server acts as a gateway and cannot get a timely response.


* * *

Pagination [​](#pagination)
---------------------------

### Overview [​](#overview)

This API implements a cursor-based pagination system, allowing clients to efficiently navigate through large datasets. The system uses a cursor parameter to manage the position and direction of pagination.

### Cursor Format [​](#cursor-format)

The cursor is a string formatted as `value:offset:is_prev`, where:

*   `value` represents the page size (number of items per page).
*   `offset` is the current page number (starting from 0).
*   `is_prev` indicates whether the cursor is moving to the previous page (`1`) or to the next page (`0`).

### Request Parameters [​](#request-parameters)

*   **`per_page` (optional)**: Number of items to display per page. Defaults to 100. The maximum allowed value specified by the server is 100.
*   **`cursor` (optional)**: Cursor string to navigate to a specific page. If not provided, pagination starts from the first page.

### Response Fields [​](#response-fields)

The paginated response includes the following fields:


|Field            |Description                                                         |
|-----------------|--------------------------------------------------------------------|
|next_cursor      |Cursor string for the next page.                                    |
|prev_cursor      |Cursor string for the previous page.                                |
|next_page_results|Boolean indicating if there are more results after the current page.|
|prev_page_results|Boolean indicating if there are results before the current page.    |
|count            |Total number of items on the current page.                          |
|total_pages      |Estimated total number of pages.                                    |
|total_results    |Total number of items across all pages.                             |
|extra_stats      |Additional statistics, if any.                                      |
|results          |Array of items for the current page.                                |


### Example: Fetching the First Page [​](#example-fetching-the-first-page)

**Request:**

```
GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/?per_page=20
```


**Response:**

json

```
{
  "next_cursor": "20:1:0",
  "prev_cursor": "",
  "next_page_results": true,
  "prev_page_results": false,
  "count": 20,
  "total_pages": 50,
  "total_results": 1000,
  "extra_stats": {},
  "results": [ ... ]
}
```


### Example: Fetching the Next Page [​](#example-fetching-the-next-page)

**Request:**

```
GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items?per_page=20&cursor=20:1:0
```


**Response:**

json

```
{
  "next_cursor": "20:2:0",
  "prev_cursor": "20:0:1",
  "next_page_results": true,
  "prev_page_results": true,
  "count": 20,
  "total_pages": 50,
  "total_results": 1000,
  "extra_stats": {},
  "results": [ ... ]
}
```


* * *

Rate Limiting [​](#rate-limiting)
---------------------------------

### Overview [​](#overview-1)

To ensure fair usage and maintain the quality of service for all users, our API implements rate limiting. Rate limiting restricts the number of requests a client can make within a certain time frame.

### Rate Limit Details [​](#rate-limit-details)

*   **Limit**: Each client is limited to 60 requests per minute.
*   **Reset Interval**: The rate limit counter resets every minute.
*   **Scope of Limitation**: The rate limit applies to all requests made with a given API key.

### Identifying Your Rate Limit Status [​](#identifying-your-rate-limit-status)

Rate limit status is communicated in the response headers of each API request:

*   **`X-RateLimit-Remaining`**: The number of requests remaining in the current rate limit window.
*   **`X-RateLimit-Reset`**: The time at which the current rate limit window resets (in UTC epoch seconds).

```
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1700327957
```


* * *

Fields and Expand Query Parameters [​](#fields-and-expand-query-parameters)
---------------------------------------------------------------------------

Our API provides flexible data retrieval capabilities through two powerful query parameters: `fields` and `expand`. These parameters allow clients to tailor the response data to their specific needs, optimizing both the payload size and the clarity of the response.

### Fields Parameter [​](#fields-parameter)

The `fields` parameter enables clients to selectively retrieve only a subset of fields for a given resource. This is particularly useful for minimizing response size and bandwidth consumption, especially when the client requires only specific pieces of data.

**Usage:**

The `fields` parameter accepts a comma-separated list of field names that the client wants to be included in the response.

```
GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/?fields=id,name,description
```


In this example, the API will return only the `id`, `name`, and `description` fields of the resource.

### Expand Parameter [​](#expand-parameter)

The `expand` parameter allows clients to request additional related information to be included in the response. This is useful for retrieving detailed information about nested resources without making separate API calls.

**Usage:**

The `expand` parameter can be used to include details of related resources or nested objects in the response.

```
GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/?expand=assignees,state
```


This request will return the resource data along with expanded information about the `assignees` and `state`.

### Error Handling [​](#error-handling-1)

*   Invalid or unrecognized field names passed in the `fields` parameter will result in an error response, indicating which fields are invalid.
*   Similarly, if `expand` is used on fields that cannot be expanded, an appropriate error message will be returned.
