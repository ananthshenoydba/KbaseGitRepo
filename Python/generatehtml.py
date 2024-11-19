from datetime import datetime, timedelta

# Function to check if a given date is a weekday
def is_weekday(date):
    return date.weekday() < 5

# Start date (June 3, 2024)
start_date = datetime(2024, 6, 3)

# End date (June 12, 2024)
end_date = datetime(2024, 6, 12)

# List of weekdays
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

# Generate the HTML table
html_table = """
<!DOCTYPE html>
<html>
<head>
  <title>June 2024 Schedule</title>
</head>
<body>
  <table>
    <thead>
      <tr>
        <th>Date</th>
        <th>7:30am - 9:00am</th>
        <th>8:00am - 9:00am</th>
        <th>3:30pm - 4:30pm</th>
        <th>3:30pm - 5:30pm</th>
        <th>3:30pm - 6:00pm</th>
      </tr>
    </thead>
    <tbody>
"""

# Loop through each day and generate table rows for weekdays
current_date = start_date
while current_date <= end_date:
    if is_weekday(current_date):
        formatted_date = current_date.strftime('%A %d %B')
        html_table += f"""
        <tr>
          <td>{formatted_date}</td>
          <td>
            <input type="checkbox" id="child1_{current_date.strftime('%Y%m%d')}_730" name="child1_breakfast" onclick="toggleCheckboxes(this, 'child1', 'breakfast')">
            <label for="child1_{current_date.strftime('%Y%m%d')}_730">1st Child</label>
            <input type="checkbox" id="child2_{current_date.strftime('%Y%m%d')}_730" name="child2_breakfast" onclick="toggleCheckboxes(this, 'child2', 'breakfast')">
            <label for="child2_{current_date.strftime('%Y%m%d')}_730">2nd Child</label>
            <input type="checkbox" id="child3_{current_date.strftime('%Y%m%d')}_730" name="child3_breakfast" onclick="toggleCheckboxes(this, 'child3', 'breakfast')">
            <label for="child3_{current_date.strftime('%Y%m%d')}_730">3rd Child</label>
          </td>
          <td>
            <input type="checkbox" id="child1_{current_date.strftime('%Y%m%d')}_800" name="child1_breakfast" onclick="toggleCheckboxes(this, 'child1', 'breakfast')">
            <label for="child1_{current_date.strftime('%Y%m%d')}_800">1st Child</label>
            <input type="checkbox" id="child2_{current_date.strftime('%Y%m%d')}_800" name="child2_breakfast" onclick="toggleCheckboxes(this, 'child2', 'breakfast')">
            <label for="child2_{current_date.strftime('%Y%m%d')}_800">2nd Child</label>
            <input type="checkbox" id="child3_{current_date.strftime('%Y%m%d')}_800" name="child3_breakfast" onclick="toggleCheckboxes(this, 'child3', 'breakfast')">
            <label for="child3_{current_date.strftime('%Y%m%d')}_800">3rd Child</label>
          </td>
          <td>
            <input type="checkbox" id="child1_{current_date.strftime('%Y%m%d')}_1530" name="child1_afterschool" onclick="toggleCheckboxes(this, 'child1', 'afterschool')">
            <label for="child1_{current_date.strftime('%Y%m%d')}_1530">1st Child</label>
            <input type="checkbox" id="child2_{current_date.strftime('%Y%m%d')}_1530" name="child2_afterschool" onclick="toggleCheckboxes(this, 'child2', 'afterschool')">
            <label for="child2_{current_date.strftime('%Y%m%d')}_1530">2nd Child</label>
            <input type="checkbox" id="child3_{current_date.strftime('%Y%m%d')}_1530" name="child3_afterschool" onclick="toggleCheckboxes(this, 'child3', 'afterschool')">
            <label for="child3_{current_date.strftime('%Y%m%d')}_1530">3rd Child</label>
          </td>
          <td>
            <input type="checkbox" id="child1_{current_date.strftime('%Y%m%d')}_1730" name="child1_afterschool" onclick="toggleCheckboxes(this, 'child1', 'afterschool')">
            <label for="child1_{current_date.strftime('%Y%m%d')}_1730">1st Child</label>
            <input type="checkbox" id="child2_{current_date.strftime('%Y%m%d')}_1730" name="child2_afterschool" onclick="toggleCheckboxes(this, 'child2', 'afterschool')">
            <label for="child2_{current_date.strftime('%Y%m%d')}_1730">2nd Child</label>
            <input type="checkbox" id="child3_{current_date.strftime('%Y%m%d')}_1730" name="child3_afterschool" onclick="toggleCheckboxes(this, 'child3', 'afterschool')">
            <label for="child3_{current_date.strftime('%Y%m%d')}_1730">3rd Child</label>
          </td>
          <td>
            <input type="checkbox" id="child1_{current_date.strftime('%Y%m%d')}_1800" name="child1_afterschool" onclick="toggleCheckboxes(this, 'child1', 'afterschool')">
            <label for="child1_{current_date.strftime('%Y%m%d')}_1800">1st Child</label>
            <input type="checkbox" id="child2_{current_date.strftime('%Y%m%d')}_1800" name="child2_afterschool" onclick="toggleCheckboxes(this, 'child2', 'afterschool')">
            <label for="child2_{current_date.strftime('%Y%m%d')}_1800">2nd Child</label>
            <input type="checkbox" id="child3_{current_date.strftime('%Y%m%d')}_1800" name="child3_afterschool" onclick="toggleCheckboxes(this, 'child3', 'afterschool')">
            <label for="child3_{current_date.strftime('%Y%m%d')}_1800">3rd Child</label>
          </td>
        </tr>
        """
    current_date += timedelta(days=1)

html_table += """
    </tbody>
  </table>
</body>
</html>
"""

# Print or save the HTML table
print(html_table)

