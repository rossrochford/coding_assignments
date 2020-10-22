import React from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";

import './App.css';

import { HomeView } from './view_components/homeView.js';
import { MovieDetailView } from './view_components/movieDetailView.js';
import { SearchResultsView } from './view_components/searchResultsView.js';

function App() {
  return (
    <Router>
      <div>
        <Switch>
          <Route exact path="/" component={HomeView} />
          <Route exact path="/search-results/:queryString" component={SearchResultsView} />
          <Route exact path="/movie/:movieId(\d+)" component={MovieDetailView} />
        </Switch>
      </div>
    </Router>
  );
}



export default App;
