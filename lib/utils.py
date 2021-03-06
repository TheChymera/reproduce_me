def float_to_tex(f,
	max_len=4,
	condensed=False,
	padding=False,
	):
	"""Reformat float to tex syntax
	Parameters
	----------
	f : float
		Float to format.
	max_len : int
		Maximum digit length of output strings.
	"""
	if condensed:
		model_str="{}\\!\\times\\!10^{{{}}}"
	else:
		model_str="{} \\times 10^{{{}}}"


	if f >= 10**-max_len and f <= 10**max_len:
		if f < -1 or f > 1:
			f_str_template = "{{:.{}g}}".format(max_len)
		if f >= -1 and f <= 1:
			f_str_template = "{{:.{}g}}".format(2)
		f_str = f_str_template.format(f)
	else:
		f_str = "{:e}".format(f)
		f_decimals, f_exponent = f_str.split("e")
		truncated_decimals = f_decimals[:max_len].rstrip('.')
		f_str = model_str.format(truncated_decimals,int(f_exponent))
	if padding:
		return '$'+f_str+'$'
	return f_str

def inline_anova(anova,
	factor=None,
	style="python",
	max_len=4,
	condensed=False,
	pythontex_safe=False,
	):
	"""Typeset factor summary from statsmodels-style anova DataFrame for inline mention.

	Parameters
	----------
	df : pandas.DataFrame or statsmodels.ContrastResults
		Pandas DataFrame object containing an ANOVA summary, or Statsmodels ContrastResults object containing an F-contrast.
	factor : str, optional
		String indicating the factor of interest from the summary given by `df`.
	max_len : int
		Maximum digit length of output strings.
	style : {"python", "tex"}, optional
		What formatting to apply to the string. A simple Python compatible string is returned when selecting "python", whereas a fancier output (decorated with TeX syntax) is returned if selecting "tex".
	"""

	if style == "python":
		try:
			inline = "F({:g},{:g})={:2G}, p={:3G}".format(
				anova["df"][factor],
				anova["df"]["Residual"],
				anova["F"][factor],
				anova["PR(>F)"][factor],
				)
		except TypeError:
			inline = "F({:g},{:g})={:2G}, p={:3G}".format(
				anova.df_num,
				anova.df_denom,
				anova.fvalue[0][0],
				anova.pvalue,
				)
	elif style == "tex":
		if condensed:
			string_template = "$F_{{{},{}}}\!=\!{},\\, p\!=\!{}$"
		else:
			string_template = "$F_{{{},{}}}={},\\, p={}$"
		try:
			degrees_of_freedom = float_to_tex(anova["df"][factor], max_len=max_len)
			degrees_of_freedom_rest = float_to_tex(anova["df"]["Residual"], max_len=max_len)
			f_string = float_to_tex(anova["F"][factor], max_len=max_len, condensed=condensed)
			p_string = float_to_tex(anova["PR(>F)"][factor], max_len=max_len, condensed=condensed)
		except TypeError:
			degrees_of_freedom = float_to_tex(anova.df_num, max_len=max_len)
			degrees_of_freedom_rest = float_to_tex(anova.df_denom, max_len=max_len)
			f_string = float_to_tex(anova.fvalue[0][0], max_len=max_len, condensed=condensed)
			p_string = float_to_tex(float(anova.pvalue), max_len=max_len, condensed=condensed)
		inline = string_template.format(
			degrees_of_freedom,
			degrees_of_freedom_rest,
			f_string,
			p_string,
			)
		if pythontex_safe:
			inline = inline.replace("\\","\\\\")
	return inline

def bold_max_row_value(df, df_tex: str):
    """
    Detect numeric values in a pandas dataframe LaTeX string (as produced by df.to_latex()), and highlight the largest
    value of each row by wrapping it with a LaTeX bold tag (\textbf{}).
    The dataframe body is selected from the tabular LaTeX environment by extracting the lines between \midrule and
    \bottomrule.


    Parameters
    ----------
    df :  pandas.DataFrame
            Pandas DataFrame object containing at least one column with only numerical values.

    df_tex: string
                String as returned by df.to_latex(). The values in this string will be changed such that the maximum
                values of each row will be bold in the resulting pdf. Note that if the maximum value of a row appears
                anywhere else in the row, as a value or a string, it will be highlighted as well (see the second
                example below).

    >>> import pandas as pd
    >>> df = pd.DataFrame({'col1': [1, 2, 20], 'col2': [3, 4, 8],'col3': [5, 6, 5]})
    >>> print(bold_max_value(df, df.to_latex()), end="")
    \\begin{tabular}{lrrr}
    \\toprule
    {} &  col1 &  col2 &  col3 \\\\
    \\midrule
    0 &     1 &     3 &     \\textbf{5} \\\\
    1 &     2 &     4 &     \\textbf{6} \\\\
    2 &    \\textbf{20} &     8 &     5 \\\\
    \\bottomrule
    \\end{tabular}


    >>> df = pd.DataFrame({'col1': [1, 2, 20], 'col2': [3, 4, 8],'col3': [5, 6, 5], 'col4': ['2015.02.04', '2016.03.05', '1912.06.12']})
    >>> print(bold_max_value(df, df.to_latex()), end="")
    \\begin{tabular}{lrrrl}
    \\toprule
    {} &  col1 &  col2 &  col3 &        col4 \\\\
    \\midrule
    0 &     1 &     3 &     \\textbf{5} &  201\\textbf{5}.02.04 \\\\
    1 &     2 &     4 &     \\textbf{6} &  201\\textbf{6}.03.05 \\\\
    2 &    \\textbf{20} &     8 &     5 &  1912.06.12 \\\\
    \\bottomrule
    \\end{tabular}
    """
    header = df_tex.find(r'\midrule') + len('\midrule\n')
    tail = df_tex.find('\n\\bottomrule')
    body = df_tex[header:tail].split('\n')
    for row_idx, (row_max, tex_row) in enumerate(zip(df.max(numeric_only=True, axis=1).values.tolist(), body)):
        body[row_idx] = tex_row.replace(str(row_max), r'\textbf{' + str(row_max) + r'}')

    return df_tex[:header] + '\n'.join(body) + df_tex[tail:]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
