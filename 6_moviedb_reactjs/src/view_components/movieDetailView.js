import React from 'react';

import { MOVIEDB_GET_MOVIE_URL, MOVIEDB_POSTER_URL } from '../util/movieDBApi.js'

import axios from 'axios';

export class MovieDetailView extends React.Component {
  
    constructor(props) {
      super(props);
      this.state = {
        movieData: null,
        // we make note of which type of response is in use because the 
        // json from '/movie/search' and '/movie/<id>' are slightly different.
        // In typescript we might declare two types for these.
        responseType: ""
      }
    }
  
    getPosterUrl() {
      if (this.state.movieData["poster_path"] == null) {
          return null;
      }
      let posterUrl = MOVIEDB_POSTER_URL.replace("{poster_path}", this.state.movieData["poster_path"]);
      return posterUrl;
    }
  
    getVotePercentage() {
      let voteAvg = this.state.movieData["vote_average"];
      return Math.round(voteAvg * 10.0);
    }

    setPageTitle() {
        let movieTitle = this.state.movieData["title"];
        document.title = "Movie: " + movieTitle;
    }
  
    componentDidMount() {
      // if movieData was passed from previous Link, use that, otherwise issue GET request to /movie/<id>
      if (this.props.location.query !== undefined) {
        this.setState({
          movieData: this.props.location.query.movieData,
          responseType: "movie_search_result"
        }, this.setPageTitle);
        return;
      }
  
      let movieId = this.props.match.params.movieId;
      let url = MOVIEDB_GET_MOVIE_URL.replace("{movie_id}", movieId);
      axios.get(url)
      .then(resp => {
        this.setState({
          movieData: resp.data,
          responseType: "movie_detail_result"
        }, this.setPageTitle);
      });
    }
  
    render() {
      if (this.state.movieData === null) {
        return (
          <div><h2>loading movie data...</h2></div>
        );      
      }
      return (
        <div>
          <h2>{ this.state.movieData["title"] }</h2>
          <p>Rating: { this.getVotePercentage() }%</p>
          <p>{ this.state.movieData["overview"] }</p>
          <div className="poster">
            {this.state.movieData["poster_path"] && <img src={this.getPosterUrl()} alt="movie poster" width="33%" height="33%" />};
          </div>          
        </div>
      );
    }
  }