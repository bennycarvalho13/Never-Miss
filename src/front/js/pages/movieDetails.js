import React, { useState, useEffect, useContext } from "react";
import PropTypes from "prop-types";
import { Link, useParams } from "react-router-dom";
import { Context } from "../store/appContext";

export const Details = props => {
	const { store, actions } = useContext(Context);
	const params = useParams();

	const [info, setInfo ] = useState([]);

	useEffect(() => {
		getInfo();

	}, []);
	
	const getInfo = () => 
	{
		console.log(params.type)
		const options = {
			method: 'GET',
			headers: {
			  accept: 'application/json',
			  Authorization: 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1NjJjYjAxZWFiNThjNGRlNzdjOWNhMmY0ZGM4ODQ0NyIsInN1YiI6IjY1Mzk1YmFhZWM0NTUyMDBlYTRkNDMxYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.cz3I9EbEUfEny1vJHlbpG7zW_2dSZRBsGCrx6Xy3768'
			}
		  };

		  fetch(`https://api.themoviedb.org/3/${params.type}/${params.theid}?language=en-US`, options)
			.then(response => response.json())
			.then(response => {console.log(response); setInfo(response)})
			.catch(err => console.error(err));
	}

	return (params.type == "movie" ?
		<div className="text-center mt-5 text-light">
			<h1 className="text-white-50 fw-bold">{info.original_title}</h1>
			<div className="row justify-content-start mt-5">
				<div className="col-2 bg-success rounded offset-2">
					<p className="text-start text-light text-center h5">
						Release : {info.release_date}
					</p>
				</div>
				<div className="col-2 bg-warning ms-2 rounded">
					<p className="text-start text-light text-center h5">
					Rating : {info.adult ? "R" : "PG"}
					</p>
				</div>
				<div className="col-2 bg-info mx-2 rounded">
					<p className="text-start text-light text-center h5">
						Duration : {info.runtime} minutes
					</p>
				</div>
			</div>
			<div className="row justify-content-start mt-5">
				<div className="col-1 bg-success bg-opacity-50 rounded offset-md-2">
					<p className="text-start text-light text-center h4">
						Synopsis
					</p>
				</div>
			</div>
			<div className="row justify-content-center">
				<div className="col-8 bg-success rounded p-2">
					<p className="text-start">
					{info.overview}
					</p>
				</div>
			</div>
		</div>
		:
		<div className="text-center mt-5 text-light">
			<h1 className="text-white-50 fw-bold">{info.name}</h1>
			<div className="row justify-content-center mt-5">
				<div className="col-2 bg-success rounded">
					<p className="text-start text-light text-center h5">
						Release : {info.first_air_date}
					</p>
				</div>
				<div className="col-2 bg-warning ms-2 rounded">
					<p className="text-start text-light text-center h5">
					Rating : {info.adult ? "R" : "PG"}
					</p>
				</div>
				<div className="col-2 bg-primary bg-opacity-50 ms-2 rounded">
					<p className="text-start text-light text-center h5">
						Episodes : {info.number_of_episodes}
					</p>
				</div>
				<div className="col-2 bg-info bg-opacity-50 ms-2 rounded">
					<p className="text-start text-light text-center h5">
						Seasons : {info.number_of_seasons}
					</p>
				</div>
			</div>
			<div className="row justify-content-start mt-5">
				<div className="col-1 bg-success bg-opacity-50 rounded offset-md-2">
					<p className="text-start text-light text-center h4">
						Synopsis
					</p>
				</div>
				<div className="col-1 bg-success bg-opacity-50 mx-2 rounded">
					<p className="text-start text-light text-center h4">
						Episodes
					</p>
				</div>
			</div>
			<div className="row justify-content-center">
				<div className="col-8 bg-success rounded p-2">
					<p className="text-start">
					{info.overview}
					</p>
				</div>
			</div>
		</div>
);
};

Details.propTypes = {
	match: PropTypes.object
};