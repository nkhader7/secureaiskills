export function renderProfile(user) {
  document.getElementById('profile').innerHTML = user.bio;
}

export function SearchResult(props) {
  return <div dangerouslySetInnerHTML={{ __html: props.query }} />;
}
