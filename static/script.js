
function confirmDelete() {
  return confirm("Are you sure you want to delete this event?");
}
function confirmDeleteAttendee() {
  return confirm("Are you sure you want to delete this attendee?");
}
function validateEventForm() {
  const title = document.getElementById('title').value.trim();
  const date = document.getElementById('date').value.trim();
 const capacity = document.getElementById('capacity').value.trim();

   if (!title) { alert('Please enter event title'); return false; }
  if (!date)  { alert('Please select a date'); return false; }
  if (capacity === '' || isNaN(capacity) || Number(capacity) <= 0) {
    alert('Please enter a valid capacity (>0)');
    return false;
  }
  return true;
}
function validateAttendeeForm() {
  const name = document.getElementById('name').value.trim();
  const email = document.getElementById('email').value.trim();
  if (!name) { alert('Enter attendee name'); return false; }
  if (!email) { alert('Enter attendee email'); return false; }

  return true;
}
function submitEventSearch(){
  document.getElementById('searchForm').submit();
  return false;
}
