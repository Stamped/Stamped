//
//  EGORefreshTableHeaderView.m
//  Demo
//
//  Created by Devin Doty on 10/14/09October14.
//  Copyright 2009 enormego. All rights reserved.
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy
//  of this software and associated documentation files (the "Software"), to deal
//  in the Software without restriction, including without limitation the rights
//  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//  copies of the Software, and to permit persons to whom the Software is
//  furnished to do so, subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in
//  all copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
//  THE SOFTWARE.
//

#import "EGORefreshTableHeaderView.h"

#define kFlipAnimationDuration 0.18f
#define kPullRefreshOffset 50.0f

@interface EGORefreshTableHeaderView (Private)
- (void)setState:(EGOPullRefreshState)aState;
@end

@implementation EGORefreshTableHeaderView

@synthesize delegate=_delegate;
@synthesize tableInset=_tableInset;
@synthesize showingSearch=_showingSearch;

- (id)initWithFrame:(CGRect)frame {
    
    if (self = [super initWithFrame:frame]) {
        
        self.backgroundColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
        self.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        self.tableInset = UIEdgeInsetsZero;

        UIImage *image = [UIImage imageNamed:@"shelf_background.png"];
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        [self addSubview:imageView];
        [imageView release];
        _shelftView = imageView;

        CGRect frame = imageView.frame;
        frame.origin.y = (self.bounds.size.height - frame.size.height);
        frame.size.width = self.bounds.size.width;
        imageView.frame = frame;
        
        UIFont *font = [UIFont boldSystemFontOfSize:12];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake((self.bounds.size.width/2), ((self.bounds.size.height-font.lineHeight)/2), 0.0f, 0.0f)];
        label.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithRed:0.600f green:0.600f blue:0.600f alpha:1.0f];
        label.shadowOffset = CGSizeMake(0.0f, 1.0f);
        label.shadowColor = [UIColor colorWithWhite:1.0f alpha:0.6f];
        label.font = font;
        [self addSubview:label];
        _titleLabel = label;
        [label release];
		
		UIActivityIndicatorView *activityView = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
        activityView.frame = CGRectMake(floorf((self.bounds.size.width/2) - 7.0f), floorf((self.bounds.size.height/2) - 7.0f), 14.0f, 14.0f);
        activityView.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin;
		[self addSubview:activityView];
		_activityView = activityView;
        [activityView release];
        
        imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"refresh_arrow.png"]];
        [self addSubview:imageView];
        _arrowView = imageView;
        
        frame = imageView.frame;
        frame.origin.y = 6.0f;
        frame.origin.x = 60.0f;
        imageView.frame = frame;
        [imageView release];

        _triggerOffset = -(kPullRefreshOffset+5);
		[self setState:EGOOPullRefreshNormal];
                
        
    }
    return self;	
}

- (void)dealloc {
	
	_delegate=nil;
	_activityView = nil;
	_arrowView = nil;
    [super dealloc];
}


#pragma mark - Setters

- (void)setTableInset:(UIEdgeInsets)tableInset {
    _tableInset = tableInset;
    _triggerOffset = (tableInset.top + (kPullRefreshOffset+5)) * -1;
}

- (void)showActivity:(BOOL)show {
    
    _arrowView.hidden = show;

    if (show) {
        
        if (![_activityView isAnimating]) {
            
            [_activityView startAnimating];
            _activityView.transform = CGAffineTransformMakeScale(0.01f, 0.01f);
            [UIView animateWithDuration:0.1f animations:^{
                _activityView.transform = CGAffineTransformMakeScale(1.0f, 1.0f);
            }];
            
        }
        
        
    } else {
     
        if ([_activityView isAnimating]) {
            
            [UIView animateWithDuration:0.1f animations:^{
                _activityView.transform = CGAffineTransformMakeScale(0.01f, 0.01f);
            } completion:^(BOOL finished) {                
                [_activityView stopAnimating];
            }];
            
        }
    }
    
}

- (void)setState:(EGOPullRefreshState)aState {
	        
    
    
	switch (aState) {
		case EGOOPullRefreshPulling: {
            
            CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"transform.rotation.z"];
            animation.fromValue = [_arrowView.layer valueForKeyPath:@"transform.rotation.z"];
            animation.toValue = [NSNumber numberWithFloat:(M_PI / 180.0) * 180.0f];
            animation.duration = kFlipAnimationDuration;
            [_arrowView.layer addAnimation:animation forKey:nil];
            [_arrowView.layer setValue:[NSNumber numberWithFloat:(M_PI / 180.0) * 180.0f] forKeyPath:@"transform.rotation.z"];

            [_titleLabel setText:NSLocalizedString(@"Release to refresh...", nil)];

        } break;
		case EGOOPullRefreshNormal:
            
            if (_state == EGOOPullRefreshPulling) {
                
                CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"transform.rotation.z"];
                animation.fromValue = [_arrowView.layer valueForKeyPath:@"transform.rotation.z"];
                animation.toValue = [NSNumber numberWithFloat:0.0f];
                animation.duration = kFlipAnimationDuration;
                [_arrowView.layer addAnimation:animation forKey:nil];
                [_arrowView.layer setValue:[NSNumber numberWithFloat:0.0f] forKeyPath:@"transform.rotation.z"];
                
            }
			
             [_titleLabel setText:NSLocalizedString(@"Pull down to refresh...", nil)];
            _titleLabel.hidden = NO;
            [self showActivity:NO];
            
			break;
		case EGOOPullRefreshLoading:
			
            [_titleLabel setText:NSLocalizedString(@"Refreshing...", nil)];
            _titleLabel.hidden = YES;
            [self showActivity:YES];
			
			break;
		default:
			break;
	}
	
    [_titleLabel sizeToFit];
    CGRect frame = _titleLabel.frame;
    frame.origin.x = (self.bounds.size.width-frame.size.width)/2;
    _titleLabel.frame = frame;
	_state = aState;
    
}

- (void)setDelegate:(id<EGORefreshTableHeaderDelegate>)delegate {
    
    _delegate = delegate;
    
    _refreshFlags.delegateRefreshTableHeaderDidTriggerRefresh = [(id)_delegate respondsToSelector:@selector(egoRefreshTableHeaderDidTriggerRefresh:)];
    _refreshFlags.delegateRefreshTableHeaderDidTriggerRefresh = [(id)_delegate respondsToSelector:@selector(egoRefreshTableHeaderDataSourceIsLoading:)];
    _refreshFlags.delegateDataSourceIsEmpty = [(id)_delegate respondsToSelector:@selector(dataSourceIsEmpty)];
    
}

- (void)setShowingSearch:(BOOL)showingSearch {
    _showingSearch=showingSearch;
    
    
    UIImage *image = [UIImage imageNamed:_showingSearch ? @"shelf_search_bg.png" : @"shelf_background.png"];
    _shelftView.image = [image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0];
    
    CGRect frame = _shelftView.frame;
    frame.origin.y = (self.bounds.size.height-frame.size.height);
    frame.size.width = self.bounds.size.width;
    _shelftView.frame = frame;
    
}


#pragma mark - ScrollView Methods

- (void)egoRefreshScrollViewDidScroll:(UIScrollView *)scrollView {
    
	if (_state == EGOOPullRefreshLoading) {
		
		CGFloat offset = MAX(scrollView.contentOffset.y * -1, 0);
		offset = MIN(offset, _tableInset.top + kPullRefreshOffset);
		scrollView.contentInset = UIEdgeInsetsMake(offset, 0.0f, 0.0f, 0.0f);

        _titleLabel.alpha = (((scrollView.contentOffset.y*-1)-16)/30);
		
	} else if (scrollView.isDragging) {
		
		BOOL _loading = NO;
        if (_refreshFlags.delegateRefreshTableHeaderDataSourceIsLoading) {
            _loading = [_delegate egoRefreshTableHeaderDataSourceIsLoading:self];
        }
		
		if (_state == EGOOPullRefreshPulling && scrollView.contentOffset.y > _triggerOffset && scrollView.contentOffset.y < 0.0f && !_loading) {
			[self setState:EGOOPullRefreshNormal];
		} else if (_state == EGOOPullRefreshNormal && scrollView.contentOffset.y < _triggerOffset && !_loading) {
			[self setState:EGOOPullRefreshPulling];
		}
		
		if (scrollView.contentInset.top != 0) {
			scrollView.contentInset = self.tableInset;
		}
	
	}
    
    if ((scrollView.contentOffset.y < 0.0f && [scrollView isDragging]) || [scrollView isDecelerating]) {

        _titleLabel.alpha = (((scrollView.contentOffset.y*-1)-16)/30);

    }
	
}

- (void)egoRefreshScrollViewDidEndDragging:(UIScrollView *)scrollView {
    
	BOOL _loading = NO;
    if (_refreshFlags.delegateRefreshTableHeaderDataSourceIsLoading) {
        _loading = [_delegate egoRefreshTableHeaderDataSourceIsLoading:self];
    }
    
	if (scrollView.contentOffset.y <= _triggerOffset && !_loading) {
		
        if (_refreshFlags.delegateRefreshTableHeaderDidTriggerRefresh) {
            [_delegate egoRefreshTableHeaderDidTriggerRefresh:self];
        }
		
		[self setState:EGOOPullRefreshLoading];
        [UIView animateWithDuration:0.2f animations:^{
            scrollView.contentInset = UIEdgeInsetsMake(self.tableInset.top + kPullRefreshOffset, 0.0f, 0.0f, 0.0f);
        }];

	}
	
}

- (void)egoRefreshScrollViewDataSourceDidFinishedLoading:(UIScrollView *)scrollView {	
	
    [UIView animateWithDuration:0.3f animations:^{
        [scrollView setContentInset:self.tableInset];
    }];
	[self setState:EGOOPullRefreshNormal];

}

- (void)updateRefreshState:(UIScrollView*)scrollView {
	
    BOOL _empty = NO;
	BOOL _loading = NO;
    
    if (_refreshFlags.delegateRefreshTableHeaderDataSourceIsLoading) {
        _loading = [_delegate egoRefreshTableHeaderDataSourceIsLoading:self];
    }
    if (_refreshFlags.delegateDataSourceIsEmpty) {
        _empty = [_delegate dataSourceIsEmpty];
    }
    
    if (_loading && (_state != EGOOPullRefreshLoading) && !_empty) {
        [self setState:EGOOPullRefreshLoading];
    } else if ((_state != EGOOPullRefreshNormal) && !_loading) {
        [self setState:EGOOPullRefreshNormal];
    }
	
}


@end
