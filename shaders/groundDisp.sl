/// Referenced from github at Ncca/Renderman/Lecture5Shaders2/Noise/Noise.sl
/// https://github.com/NCCA/Renderman/blob/master/Lecture5Shaders2/Noise/Noise.sl

displacement groundDisp
(
  float Km=0.4;
  float Layers=30;
  output varying float Freq=40;
)

{
  // init the shader values
  vector NN=normalize(N);
  float i;
  float mag=0;
  point Pt=transform("shader",P);
  for(i=0; i<Layers; i+=1)
  {
    mag+=(float noise(Pt*Freq)-0.5)*2/Freq;
    Freq*=2;
  }
  mag /=length(vtransform("object",NN));
  P=P+mag*NN*Km;
  N=calculatenormal(P);
}