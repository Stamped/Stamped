
TODO:
    * get hilbert working on the web
    * get tenebrous working on the web


TEMPLATES:
    NOTE: all control-flow logic belongs in the processing code itself!
    
    /** auto <type> **/
    /** auto color  **/
    
    /** restart_on_edit  **/
    /** no_restart_on_edit  **/
    
    /** string  **/ /** endstring  **/
    /** color   **/ /** endcolor   **/
    /** float   **/ /** endfloat   **/
    /** int     **/ /** endint     **/
    /** boolean **/ /** endboolean **/
    /** char    **/ /** endchar    **/
    /** expr    **/ /** endexpr    **/
    
    /** int [ 0, 2 ] **/
    /** int [ 0, 3 ) **/
    
    /** float [ 0, 1 ) **/
    
    /** string function(s) { return s + ";" } **/
    /** string [ "s0", "s1", "s2" ] **/
    
    /** expr [ random(3, 5), 2 * random(-1, 50), (x ? 1.0 : -1.0) ] **/


TODO:
    * how to constrain alpha, hue, or etc. in /** color **/


OLD:
    /** switch **/
        /** case test0 }
            { break **/
        /** case test0 }
            { break **/
        /** default **/
            /** break **/
    /** endswitch **/

