#!/usr/bin/env fish
# Runs GYRE on all profile*.GYRE files in the LOGS directory.

source ~/.mesa_env

# Create a main directory for all gyre outputs to keep things clean
mkdir -p gyre_outputs

for profile in LOGS/*.GYRE
    if test -f "$profile"
        set base (basename "$profile" .GYRE)
        echo "Running GYRE on $profile..."
        
        # Create a dedicated directory for this specific profile
        set outdir "gyre_outputs/$base"
        mkdir -p "$outdir"
        
        # Create a customized gyre.in for this profile
        set temp_in "$outdir/gyre.in"
        
        # Use sed to dynamically replace the configuration values
        sed -e "s|^\s*file\s*=.*|  file = '$profile'|" \
            -e "s|^\s*summary_file\s*=.*|  summary_file = '$outdir/summary.h5'|" \
            -e "s|^\s*detail_template\s*=.*|  detail_template = '$outdir/detail.l%l.n%n.h5'|" \
            gyre.in > $temp_in
            
        # Ensure there is a trailing newline so Fortran can parse the final namelist!
        echo "" >> $temp_in
        
        # Run gyre on the newly customized config file
        gyre $temp_in
    end
end

echo "Done."
