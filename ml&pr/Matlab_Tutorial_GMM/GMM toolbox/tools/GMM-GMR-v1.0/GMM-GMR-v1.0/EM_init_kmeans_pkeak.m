function [Priors, Mu, Sigma] = EM_init_kmeans(Data, nbStates)
%
% This function initializes the parameters of a Gaussian Mixture Model 
% (GMM) by using k-means clustering algorithm.
%
% Inputs -----------------------------------------------------------------
%   o Data:     D x N array representing N datapoints of D dimensions.
%   o nbStates: Number K of GMM components.
% Outputs ----------------------------------------------------------------
%   o Priors:   1 x K array representing the prior probabilities of the
%               K GMM components.
%   o Mu:       D x K array representing the centers of the K GMM components.
%   o Sigma:    D x D x K array representing the covariance matrices of the 
%               K GMM components.
% Comments ---------------------------------------------------------------
%   o This function uses the 'kmeans' function from the MATLAB Statistics 
%     toolbox. If you are using a version of the 'netlab' toolbox that also
%     uses a function named 'kmeans', please rename the netlab function to
%     'kmeans_netlab.m' to avoid conflicts. 
%
% Copyright (c) 2006 Sylvain Calinon, LASA Lab, EPFL, CH-1015 Lausanne,
%               Switzerland, http://lasa.epfl.ch

[Data_id, Centers] = kmeans(Data', nbStates);
Mu = Centers';
for i=1:nbStates
  idtmp = find(Data_id==i);
  Priors(i) = length(idtmp);
  Sigma(:,:,i) = cov(Data(:,idtmp)');
end
Priors = Priors ./ sum(Priors);


