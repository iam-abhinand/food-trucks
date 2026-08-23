import { useEffect, useRef, useState } from "react";

function SearchBar({ onSearch, debounceMs = 300 }) {
  const [query, setQuery] = useState("");
  const isFirstRender = useRef(true);

  // Always holds the latest onSearch function, without needing to be
  // an effect dependency. This is what breaks the feedback loop: the
  // parent (App) can re-render and hand us a "new" onSearch function
  // as often as it wants — we just quietly track the latest one here,
  // without that causing our debounce effect to re-fire.
  const onSearchRef = useRef(onSearch);
  useEffect(() => {
    onSearchRef.current = onSearch;
  }, [onSearch]);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    const timeoutId = setTimeout(() => {
      onSearchRef.current(query);
    }, debounceMs);

    return () => clearTimeout(timeoutId);
    // Only `query` (and debounceMs, which never changes) should trigger
    // a new debounced search — not onSearch's identity.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, debounceMs]);

  function handleSubmit(event) {
    event.preventDefault();
    onSearchRef.current(query);
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Search by truck name or food type..."
      />
      <button type="submit">Search</button>
    </form>
  );
}

export default SearchBar;