import React from 'react';
import ReactDOM from 'react-dom';
import {
  BrowserRouter as Router,
  Route,
  Link
} from 'react-router-dom'
import './index.css';
import Routes from './routes';

import './index.css';

ReactDOM.render(
    <Router>
        <Routes />
    </Router>,
    document.getElementById('root')
);
