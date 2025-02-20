# Authentication API Documentation

## Endpoints

### Register User
- **URL**: `/api/auth/register/`
- **Method**: POST
- **Data**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "confirm_password": "string",
    "user_type": "CUSTOMER|OWNER",
    "first_name": "string",     // Optional
    "last_name": "string",      // Optional
    "phone_number": "string",   // Optional
    "about_me": "string",       // Optional
    "gender": "string"          // Optional (M/F/O/N)
  }
  ```
- **Success Response**: 
  - **Code**: 201 Created
  - **Content**:
    ```json
    {
      "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "user_type": "string",
        "phone_number": "string",
        "profile_picture": "url|null",
        "about_me": "string",
        "gender": "string",
        "gender_display": "string"
      },
      "message": "User Created Successfully"
    }
    ```
- **Error Response**: 400 Bad Request

### Login
- **URL**: `/api/auth/login/`
- **Method**: POST
- **Description**: Authenticates a user using email/username and password
- **Request Body**:
  ```json
  {
    "email_or_username": "string",  // Can be either email or username
    "password": "string"
  }
  ```
- **Success Response**: 
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "status": "success",
      "access": "string",      // JWT access token
      "refresh": "string",     // JWT refresh token
      "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "user_type": "string", // CUSTOMER, OWNER, or ADMIN
        "phone_number": "string",
        "profile_picture": "string|null",
        "about_me": "string",
        "gender": "string",    // M, F, O, or N
        "gender_display": "string" // Male, Female, Other, or Prefer not to say
      }
    }
    ```

- **Error Responses**:
  - **Code**: 400 Bad Request
  - **Content Examples**:
    ```json
    {
      "error": {
        "email_or_username": ["No account found with this email address."]
      }
    }
    ```
    ```json
    {
      "error": {
        "email_or_username": ["No account found with this username."]
      }
    }
    ```
    ```json
    {
      "error": {
        "error": "Invalid credentials. Please check your email/username and password."
      }
    }
    ```
    ```json
    {
      "error": {
        "error": "This account is inactive or has been disabled."
      }
    }
    ```
    ```json
    {
      "error": {
        "error": "Both email/username and password are required."
      }
    }
    ```

  - **Code**: 500 Internal Server Error
  - **Content**:
    ```json
    {
      "error": "Database error occurred. Please try again."
    }
    ```
    ```json
    {
      "error": "An unexpected error occurred. Please try again."
    }
    ```

### Notes:
- The access token should be included in the Authorization header for subsequent requests:
  ```
  Authorization: Bearer <access_token>
  ```
- The refresh token can be used to obtain a new access token when it expires
- All fields in the user object are read-only through this endpoint
- The gender field uses single-character codes with human-readable displays:
  - 'M' -> 'Male'
  - 'F' -> 'Female'
  - 'O' -> 'Other'
  - 'N' -> 'Prefer not to say'

### Refresh Token
- **URL**: `/api/auth/refresh/`
- **Method**: POST
- **Data**:
  ```json
  {
    "refresh": "string"
  }
  ```
- **Success Response**: 200 OK
  ```json
  {
    "access": "string"
  }
  ```
- **Error Response**: 401 Unauthorized

## Authentication
All protected endpoints require a Bearer token in the Authorization header: 

### User Profile Management

#### Get Profile
- **URL**: `/api/profile/`
- **Method**: GET
- **Authentication**: Required
- **Success Response**: 
  ```json
  {
    "status": "success",
    "user": {
      "id": "integer",
      "username": "string",
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "user_type": "string",
      "phone_number": "string",
      "profile_picture": "url|null",
      "about_me": "string",
      "gender": "string",
      "gender_display": "string"
    }
  }
  ```

#### Update Profile
- **URL**: `/api/profile/`
- **Method**: PATCH
- **Authentication**: Required
- **Content-Type**: multipart/form-data
- **Request Body**:
  ```json
  {
    "first_name": "string",      // Optional
    "last_name": "string",       // Optional
    "phone_number": "string",    // Optional
    "about_me": "string",        // Optional
    "gender": "string",          // Optional (M/F/O/N)
    "profile_picture": "file"    // Optional, image file
  }
  ```
- **Success Response**: 
  ```json
  {
    "status": "success",
    "message": "Profile updated successfully",
    "user": {
      "id": "integer",
      "username": "string",
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "user_type": "string",
      "phone_number": "string",
      "profile_picture": "url|null",
      "about_me": "string",
      "gender": "string",
      "gender_display": "string"
    }
  }
  ```
- **Error Response**:
  ```json
  {
    "status": "error",
    "errors": {
      "field_name": ["error message"]
    }
  }
  ``` 

# Restaurant Management API Documentation

## Base URL
All restaurant endpoints are prefixed with: `/api/restaurants/`

## Endpoints

### List Restaurants
- **URL**: `/api/restaurants/`
- **Method**: GET
- **Authentication**: Optional
- **Description**: Returns a list of restaurants. Restaurant owners see their own restaurants, staff see all restaurants, others see only approved restaurants.
- **Query Parameters**:
  - `page`: Page number for pagination
  - `search`: Search term for restaurant name/city
- **Success Response**: 
  ```json
  {
    "count": "integer",
    "next": "url|null",
    "previous": "url|null",
    "results": [
      {
        "id": "integer",
        "name": "string",
        "owner": "integer",
        "phone": "string",
        "website": "string",
        "email": "string",
        "country": "string",
        "street_address": "string",
        "room_number": "string",
        "city": "string",
        "state": "string",
        "postal_code": "string",
        "latitude": "decimal",
        "longitude": "decimal",
        "venue_types": ["string"],
        "cuisine_styles": ["string"],
        "logo": "url|null",
        "is_approved": "boolean",
        "created_at": "datetime",
        "updated_at": "datetime",
        "images": [],
        "operating_hours": [],
        "holiday_hours": [],
        "amenities": {}
      }
    ]
  }
  ```

### Create Restaurant
- **URL**: `/api/restaurants/`
- **Method**: POST
- **Authentication**: Required (Restaurant Owner only)
- **Content-Type**: multipart/form-data
- **Request Body**:
  ```json
  {
    "name": "string",
    "phone": "string",
    "website": "string (optional)",
    "email": "string",
    "country": "string",
    "street_address": "string",
    "room_number": "string (optional)",
    "city": "string",
    "state": "string",
    "postal_code": "string",
    "latitude": "decimal (optional)",
    "longitude": "decimal (optional)",
    "venue_types": ["string"],
    "cuisine_styles": ["string"],
    "logo": "file (optional)"
  }
  ```
- **Success Response**: 201 Created
- **Error Response**: 400 Bad Request

### Get Restaurant Details
- **URL**: `/api/restaurants/{id}/`
- **Method**: GET
- **Authentication**: Optional
- **Success Response**: 200 OK
  ```json
  {
    "id": "integer",
    "name": "string",
    // ... same as list response
  }
  ```

### Update Restaurant
- **URL**: `/api/restaurants/{id}/`
- **Method**: PUT/PATCH
- **Authentication**: Required (Restaurant Owner only)
- **Content-Type**: multipart/form-data
- **Request Body**: Same as Create Restaurant
- **Success Response**: 200 OK
- **Error Response**: 403 Forbidden if not owner

### Delete Restaurant
- **URL**: `/api/restaurants/{id}/`
- **Method**: DELETE
- **Authentication**: Required (Restaurant Owner only)
- **Success Response**: 204 No Content
- **Error Response**: 403 Forbidden if not owner

### Upload Restaurant Images
- **URL**: `/api/restaurants/{id}/upload_images/`
- **Method**: POST
- **Authentication**: Required (Restaurant Owner only)
- **Content-Type**: multipart/form-data
- **Request Body**:
  ```json
  {
    "images": "file[]",
    "video_url": "string (optional)",
    "is_video_thumbnail": "boolean (optional)"
  }
  ```
- **Success Response**: 201 Created
  ```json
  [
    {
      "id": "integer",
      "image": "url",
      "is_video_thumbnail": "boolean",
      "video_url": "string|null",
      "created_at": "datetime"
    }
  ]
  ```

### Set Operating Hours
- **URL**: `/api/restaurants/{id}/set_hours/`
- **Method**: POST
- **Authentication**: Required (Restaurant Owner only)
- **Request Body**:
  ```json
  {
    "operating_hours": [
      {
        "day": "MON|TUE|WED|THU|FRI|SAT|SUN",
        "open_time": "HH:MM:SS",
        "close_time": "HH:MM:SS",
        "is_closed": "boolean"
      }
    ],
    "holiday_hours": [
      {
        "holiday": "NEW_YEAR|AUSTRALIA_DAY|...",
        "open_time": "HH:MM:SS",
        "close_time": "HH:MM:SS",
        "is_closed": "boolean"
      }
    ]
  }
  ```
- **Success Response**: 200 OK
  ```json
  {
    "message": "Hours updated successfully"
  }
  ```

### Set Amenities
- **URL**: `/api/restaurants/{id}/set_amenities/`
- **Method**: POST
- **Authentication**: Required (Restaurant Owner only)
- **Request Body**:
  ```json
  {
    "general_amenities": {
      "inside_dining": "boolean",
      "outdoor_seating": "boolean",
      // ... other amenities
    },
    "entertainment_amenities": {
      "ambient_music": "boolean",
      "live_entertainment": "boolean",
      // ... other entertainment options
    },
    "bathroom_amenities": {
      "private_bathrooms": "boolean",
      // ... other bathroom amenities
    },
    "accessibility_amenities": {
      "wheelchair_accessible": "boolean",
      // ... other accessibility options
    },
    "kids_amenities": {
      "highchairs": "boolean",
      // ... other kids amenities
    },
    "parking_amenities": {
      "private_parking": "boolean",
      // ... other parking options
    },
    "special_amenities": {
      "pet_friendly": "boolean",
      // ... other special amenities
    },
    "payment_options": {
      "accepts_credit_card": "boolean",
      // ... other payment options
    },
    "takeaway_delivery_options": {
      "offers_delivery": "boolean",
      // ... other delivery options
    },
    "additional_amenities": ["string"]
  }
  ```
- **Success Response**: 200 OK

### Approve Restaurant (Staff Only)
- **URL**: `/api/restaurants/{id}/approve/`
- **Method**: POST
- **Authentication**: Required (Staff only)
- **Success Response**: 200 OK
  ```json
  {
    "message": "Restaurant approved successfully"
  }
  ```
- **Error Response**: 403 Forbidden if not staff

## Notes
- All protected endpoints require JWT authentication
- Include the token in the Authorization header:
  ```
  Authorization: Bearer <access_token>
  ```
- Image uploads should be in valid image formats (jpg, png, etc.)
- Times should be in 24-hour format
- Coordinates (latitude/longitude) should be valid decimal values 

# Restaurant Reviews API Documentation

## Menu Categories API

### List Menu Categories
Get a list of all active menu categories.

```
GET /api/menus/categories/
```

**Response (200 OK)**
```json
[
    {
        "id": 1,
        "name": "Banquets",
        "code": "banquets",
        "description": "Special group dining options for events and celebrations",
        "special_notes": "Minimum 10 people required. Please book 48 hours in advance.",
        "is_active": true
    },
    {
        "id": 2,
        "name": "Beverages",
        "code": "beverages",
        "description": "Refreshing drinks and cold beverages",
        "special_notes": "Free refills on selected soft drinks. Happy hour 4-6 PM daily.",
        "is_active": true
    }
    // ... other categories
]
```

### Get Single Category
Get details of a specific menu category.

```
GET /api/menus/categories/{category_id}/
```

**Parameters**
- `category_id`: ID of the menu category (integer)

**Response (200 OK)**
```json
{
    "id": 1,
    "name": "Banquets",
    "code": "banquets",
    "description": "Special group dining options for events and celebrations",
    "special_notes": "Minimum 10 people required. Please book 48 hours in advance.",
    "is_active": true
}
```

**Response (404 Not Found)**
```json
{
    "detail": "Menu category not found"
}
```

### Create Menu Category
Create a new menu category.

```
POST /api/menus/categories/
```

**Request Body**
```json
{
    "name": "New Category",
    "description": "Category description",
    "special_notes": "Special notes for the category",
    "is_active": true
}
```

**Response (201 Created)**
```json
{
    "id": 15,
    "name": "New Category",
    "code": "new-category",
    "description": "Category description",
    "special_notes": "Special notes for the category",
    "is_active": true
}
```

**Response (400 Bad Request)**
```json
{
    "name": ["A menu category with this name already exists."]
}
```

### Default Categories
The system comes with the following pre-defined categories:
- Banquets
- Beverages
- Bread
- Breakfast
- Desserts
- Hot Beverages
- Kids Meals
- Lunch
- Pizza
- Salads
- Sauces
- Soups
- Specials
- Starters

Each category includes:
- Unique name and code
- Description
- Special notes
- Active status
- Default flag

## Authentication
All menu category endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

## Error Responses

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 400 Bad Request
```json
{
    "field_name": ["Error message"]
}
```

## Pricing Titles API

### List Pricing Titles
Get a list of all active pricing titles.

```
GET /api/menus/pricing-titles/
```

**Response (200 OK)**
```json
[
    {
        "id": 1,
        "name": "Members",
        "code": "members",
        "description": "Special pricing for registered members",
        "display_order": 1,
        "is_active": true
    },
    {
        "id": 2,
        "name": "VIPs",
        "code": "vips",
        "description": "Exclusive pricing for VIP customers",
        "display_order": 2,
        "is_active": true
    }
    // ... other pricing titles
]
```

### Get Single Pricing Title
Get details of a specific pricing title.

```
GET /api/menus/pricing-titles/{title_id}/
```

**Parameters**
- `title_id`: ID of the pricing title (integer)

**Response (200 OK)**
```json
{
    "id": 1,
    "name": "Members",
    "code": "members",
    "description": "Special pricing for registered members",
    "display_order": 1,
    "is_active": true
}
```

### Create Pricing Title
Create a new pricing title.

```
POST /api/menus/pricing-titles/
```

**Request Body**
```json
{
    "name": "New Title",
    "description": "Description of the pricing title",
    "display_order": 5,
    "is_active": true
}
```

**Response (201 Created)**
```json
{
    "id": 5,
    "name": "New Title",
    "code": "new-title",
    "description": "Description of the pricing title",
    "display_order": 5,
    "is_active": true
}
```

### Default Pricing Titles
The system comes with the following pre-defined pricing titles:
- Members (display_order: 1)
- VIPs (display_order: 2)
- Guests (display_order: 3)
- Visitors (display_order: 4) 

## Menu Design API

### Create Menu Design
Create a new menu design for a restaurant.

```
POST /api/menus/menu-designs/
```

**Request Body**
```json
{
    "restaurant_id": 1,
    "is_multiple_pricing": true,
    "categories": [
        {
            "category_id": 1,
            "special_notes": "Breakfast served 6am- 10:30am",
            "display_order": 1
        },
        {
            "category_id": 2,
            "special_notes": "All Kids meals come with a Soft Drink or Ice Cream",
            "display_order": 2
        }
    ],
    "pricing_titles": [
        {
            "pricing_title_id": 1,
            "display_order": 1
        },
        {
            "pricing_title_id": 2,
            "display_order": 2
        }
    ]
}
```

### Get Menu Design
Get menu design for a specific restaurant.

```
GET /api/menus/menu-designs/{restaurant_id}/
```

### Update Category Order
Update the display order of menu categories.

```
PUT /api/menus/menu-designs/{restaurant_id}/categories/order/
```

### Update Pricing Order
Update the display order of pricing titles.

```
PUT /api/menus/menu-designs/{restaurant_id}/pricing/order/
``` 