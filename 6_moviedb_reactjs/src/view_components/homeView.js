import React from 'react';

export class HomeView extends React.Component {
  
    constructor(props) {
      super(props);
      this.state = {
        searchQuery: ""
      }
    }

    handleKeyUp(e) {
        if (e.keyCode === 13) {
            this.handleSearch();
            return;
        }
        this.setState({
            searchQuery: e.target.value
        });
    }
  
    handleSearch() {
      let queryString = this.state.searchQuery;
      // string cleaning needs more work e.g. removing multiple spaces
      queryString = queryString.replace("  ", " ").toLowerCase();
      let qs = encodeURIComponent(queryString).replace("%20", "+");
      this.props.history.push("/search-results/" + qs)
    }
  
    render() {
      return (
        <div>
          <h2>Movie Search</h2>
          <input type="text" onKeyUp={(e) => this.handleKeyUp(e)} />
          <button type="submit" onClick={(e) => this.handleSearch(e)}>Search</button>
        </div>
      )
    }
  }
