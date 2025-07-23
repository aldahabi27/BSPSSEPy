function satx = saturation(x, upper, lower)
    satx = x;
    for i = 1:length(x)
    if x(i) > upper(i)
        satx(i) = upper(i);
    elseif x(i) < lower(i)
        satx(i) = lower(i);
    else
        satx(i) = x(i);
    end
end