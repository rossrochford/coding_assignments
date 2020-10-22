import React from 'react';
import {
    Link
  } from "react-router-dom";

import { MOVIEDB_SEARCH_URL } from '../util/movieDBApi.js'

import axios from 'axios';

export class SearchResultsView extends React.Component {

    constructor(props) {
      super(props);
      this.state = {
        searchResults: []
      }
    }
  
    componentDidMount() {
      document.title = "Search results";
      let queryString = decodeURIComponent(this.props.match.params.queryString);
      let url = MOVIEDB_SEARCH_URL.replace("{query_string}", queryString);
      axios.get(url)
        .then(res => {
          const results = res.data.results;
          this.setState({
            searchResults: results
          });
        });
    }
  
    render() {
      return (
        <div>
          <h2>Search Results ( {this.state.searchResults.length} )</h2>
          <ul>
            {this.state.searchResults.map((value, index) => {
              return <li key={index}><Link to={{ pathname: "/movie/" + value["id"], query: {movieData: value} }}>{ value.title }</Link></li>
            })}
          </ul>
        </div>
      );
    }
  }