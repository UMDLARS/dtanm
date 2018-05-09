import React, { Component } from 'react';
import logo from './logo.svg';
import SignUp from './SignUp.js'
import SignIn from './SignIn.js'
import './App.css';

class App extends Component {
    state = {
        loggedin : false,
        signup : false
    };
    constructor(props){
        super(props);
        this.LoginEvent.bind(this);
    }

    LoginEvent(event){
        let data;
        if(this.state.signup){
            data = {
                username: event.target.username.value,
                email: event.target.email.value,
                team: event.target.team.value,
                password: event.target.password.value,
                passwordConf: event.target.passwordConf.value
            }
        } else {
            data ={
                logemail : event.target.logemail.value,
                logpassword : event.target.logpassword.value
            }
        }
        const res = async() => {
            const response = await fetch('/login', {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            const res = await response.json();

            if(res.status !== 200) throw Error(res.message);
            this.setState({loggedin : true });

            console.log(res.status);
        }

        res();
        console.log(this.state)
    }

    OnCheck(event){
        const checked = event.target.checked;
        this.setState({signup : checked});
    }

    Toggle(){
        if(!this.state.loggedin){
            return(
                <label text="SignUp" class="switch">
                  <input onClick ={this.OnCheck.bind(this)} type="checkbox"/>
                  <span class="slider"></span>
                </label>
            )
        }
        else {
            return(null);
        }
    }

    render() {
        const signup = this.state.signup;
        const signForm = signup ? (<SignUp  onLogIn={this.LoginEvent.bind(this)}/>) : (<SignIn  onLogIn={this.LoginEvent.bind(this)}/>);
        return (
            <div className="App">
            <header className="App-header">
            <img src={logo} className="App-logo" alt="logo" />
            <h1 className="App-title">Welcome to React</h1>
            </header>
                {signForm}
                {this.Toggle()}
            </div>
        );
    }
}

export default App;
