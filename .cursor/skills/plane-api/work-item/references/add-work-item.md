---
name: add-work-item
description: Create a new work item in the specified project with the provided details.
---

### Path Parameters [​](https://developers.plane.so/api-reference/issue/add-issue\#path-parameters)

`project_id`:requiredstring

The unique identifier of the project.

`workspace_slug`:requiredstring

The workspace\_slug represents the unique workspace identifier for a workspace in Plane. It can be found in the URL. For example, in the URL `https://app.plane.so/my-team/projects/`, the workspace slug is `my-team`.

### Body Parameters [​](https://developers.plane.so/api-reference/issue/add-issue\#body-parameters)

`assignees`:optionalarray

Assignees.

`labels`:optionalarray

Labels.

`type_id`:optionalstring

Type id.

`parent`:optionalstring

Parent.

`deleted_at`:optionalstring

Deleted at.

`point`:optionalinteger

Point.

`name`:requiredstring

Name.

`description_html`:optionalstring

Description html.

`description_stripped`:optionalstring

Description stripped.

`priority`:optionalstring

- `urgent` \- Urgent
- `high` \- High
- `medium` \- Medium
- `low` \- Low
- `none` \- None

`start_date`:optionalstring

Start date.

`target_date`:optionalstring

Target date.

`sequence_id`:optionalinteger

Sequence id.

`sort_order`:optionalnumber

Sort order.

`completed_at`:optionalstring

Completed at.

`archived_at`:optionalstring

Archived at.

`last_activity_at`:optionalstring

Last activity at.

`is_draft`:optionalboolean

Is draft.

`external_source`:optionalstring

External source.

`external_id`:optionalstring

External id.

`created_by`:optionalstring

Created by.

`state`:optionalstring

State.

`estimate_point`:optionalstring

Estimate point.

`type`:optionalstring

Type.

### Scopes [​](https://developers.plane.so/api-reference/issue/add-issue\#scopes)

`projects.work_items:write`

Create a work item

cURLPythonJavaScript


```bash
curl -X POST \
  "https://api.plane.so/api/v1/workspaces/my-workspace/projects/project-uuid/work-items/" \
  -H "X-API-Key: $PLANE_API_KEY" \
  # Or use -H "Authorization: Bearer $PLANE_OAUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Example Name",
  "description": "Example description",
  "priority": "medium",
  "state": "550e8400-e29b-41d4-a716-446655440000",
  "assignees": [\
    "550e8400-e29b-41d4-a716-446655440000"\
  ],
  "labels": [\
    "550e8400-e29b-41d4-a716-446655440000"\
  ],
  "external_id": "550e8400-e29b-41d4-a716-446655440000",
  "external_source": "github"
}'
```


```python
import requests

response = requests.post(
    "https://api.plane.so/api/v1/workspaces/my-workspace/projects/project-uuid/work-items/",
    headers={"X-API-Key": "your-api-key"},
    json={
      "name": "Example Name",
      "description": "Example description",
      "priority": "medium",
      "state": "550e8400-e29b-41d4-a716-446655440000",
      "assignees": [\
"550e8400-e29b-41d4-a716-446655440000"\
      ],
      "labels": [\
"550e8400-e29b-41d4-a716-446655440000"\
      ],
      "external_id": "550e8400-e29b-41d4-a716-446655440000",
      "external_source": "github"
    }
)
print(response.json())
```

```javascript
const response = await fetch("https://api.plane.so/api/v1/workspaces/my-workspace/projects/project-uuid/work-items/", {
  method: "POST",
  headers: {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    name: "Example Name",
    description: "Example description",
    priority: "medium",
    state: "550e8400-e29b-41d4-a716-446655440000",
    assignees: ["550e8400-e29b-41d4-a716-446655440000"],
    labels: ["550e8400-e29b-41d4-a716-446655440000"],
    external_id: "550e8400-e29b-41d4-a716-446655440000",
    external_source: "github",
  }),
});
const data = await response.json();
```

Response201
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Example Name",
  "description": "Example description",
  "sequence_id": 1,
  "priority": "high",
  "assignees": ["550e8400-e29b-41d4-a716-446655440000"],
  "labels": ["550e8400-e29b-41d4-a716-446655440000"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```
