//
//  EGORefreshTableFooterView.m
//  Fav.TV
//
//  Created by Devin Doty on 2/23/11.
//  Copyright 2011 enormego. All rights reserved.
//

#import "EGORefreshTableFooterView.h"

@implementation EGORefreshTableFooterView


- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {   
        
		self.backgroundColor = [UIColor clearColor];
        _footerImageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"gifture_footer_icon.png"]];
        _footerImageView.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin;
        CGRect frame = _footerImageView.frame;
        _footerImageView.frame = CGRectMake((self.bounds.size.width-frame.size.width)/2, (self.bounds.size.height-frame.size.height)/2, frame.size.width, frame.size.height);
        [self addSubview:_footerImageView];
        
    }
    return self;
}


#pragma mark - Setters

- (void)showShadow:(BOOL)show{
	
    return;
    
	if (show) {
		
		if (!_shadowView) {
			
			UIImageView *view = [[UIImageView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.bounds.size.width, 7.0f)];
			view.image = [[UIImage imageNamed:@"show_shadow.png"] stretchableImageWithLeftCapWidth:1.0f topCapHeight:0.0f];
			view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin;
			[self addSubview:view];
			_shadowView = view;
			view.alpha=0.01f;
            [view release];
			
		}
		
		[UIView animateWithDuration:0.2f animations:^{
			_shadowView.alpha = 1.0f;
		}];
		
		
	} else {
		
		if(_shadowView){
			[_shadowView removeFromSuperview];
			_shadowView=nil;
		}
		
	}

	
}

- (void)setLoading:(BOOL)loading{
	
    _footerImageView.hidden = loading;

	if (loading) {
		
		if (!_activity) {
			
			UIActivityIndicatorView *view = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
            view.frame = CGRectMake(floor((self.bounds.size.width/2) - 7.0f), floor((self.bounds.size.height/2) - 7.0f), 14.0f, 14.0f);
            view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
			[self addSubview:view];
			_activity=view;
            [view release];
		}
		
		[_activity startAnimating];
		
	} else {

    
        /*
		if (!_endLabel) {
			
            //BOOL _retina = ([[UIScreen mainScreen] scale] >= 2.0);
            UIFont *font = [UIFont fontWithName:@"BodoniOrnamentsITCTT" size:18];// [UIFont boldSystemFontOfSize:_retina ? 18 : 16];
            UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
            label.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleBottomMargin;
            label.font = font;
            label.shadowColor = [UIColor whiteColor];
            label.shadowOffset = CGSizeMake(0.0f, 1.0f);
            label.textAlignment = UITextAlignmentCenter;
            label.backgroundColor = [UIColor clearColor];
            label.textColor = [UIColor colorWithWhite:0.82 alpha:1.0f];
            label.text = @"f";
            [label sizeToFit];
            
            CGRect frame = label.frame;
            frame.origin.x = (self.bounds.size.width-frame.size.width)/2;
            frame.origin.y = 6.0f;
            label.frame = frame;
			[self addSubview:label];
			_endLabel = label;
			
		}
		*/
        
		if (_activity) {
			[_activity removeFromSuperview];
			_activity=nil;
		}
		
	}

	
}


#pragma mark - Dealloc

- (void)dealloc {
	_endLabel=nil;
	_shadowView=nil;
	_activity=nil;
    _footerImageView=nil;
    [super dealloc];
}


@end
