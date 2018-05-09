import React, { Component } from 'react';

class SignUp extends Component{
    constructor(props){
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
    }
    handleSubmit(event){
        // alert("ASDASD");
        // alert(event.target.username.value)
        event.preventDefault();
        this.props.onLogIn(event);
    }
    render() {
        return(
            <div>
                <form onSubmit={this.handleSubmit}>
                    Username:
                        <input type="text" id="username" name="username"/> <br/>
                    Email:
                        <input type="text" id="email" name="email"/> <br/>
                    Team:
                        <input type="text" id="team" name="team" /> <br/>
                    Password:
                        <input type="password" id="password" name="password" /> <br/>
                    Confirm Password:
                        <input type="password" id="passwordConf" name="passwordConf" /> <br/>
                    <button type="submit" value="Submit"> Submit </button>
                </form>
            </div>
        )
    }
}

export default SignUp;
