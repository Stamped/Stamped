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
//#import "GiftureRefreshPatternView.h"

#define TEXT_COLOR	 [UIColor colorWithRed:87.0/255.0 green:108.0/255.0 blue:137.0/255.0 alpha:1.0]
#define FLIP_ANIMATION_DURATION 0.18f
#define kPullRefreshOffset 50.0f

@interface EGORefreshShadowView : UIView
@end
@implementation EGORefreshShadowView

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        self.backgroundColor = [UIColor clearColor];
    }
    return self;
}

- (void)drawRect:(CGRect)rect {
    
    [[UIColor grayColor] setStroke];
    
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGContextMoveToPoint(ctx, 0.0f, -3.0f);
    CGContextAddQuadCurveToPoint(ctx, self.bounds.size.width/2, self.bounds.size.height-1.0f, self.bounds.size.width, -3.0f);
    
    CGContextSetShadowWithColor(ctx, CGSizeMake(0.0f, 1.0f), 2.0f, [UIColor grayColor].CGColor);
    CGContextStrokePath(ctx);
    
    CGContextSetShadow(ctx, CGSizeMake(0.0f, 0.0f), 0.0f);
    [[UIColor colorWithWhite:0.7f alpha:0.6] setStroke];
    CGContextMoveToPoint(ctx, 0.0f, 0.0f);
    CGContextAddLineToPoint(ctx, rect.size.width, 0.0f);
    CGContextStrokePath(ctx);

}

@end


@interface EGORefreshArrowView : UIView {
@private
    CALayer  *_pullArrow;
}
@property(nonatomic,assign,getter=isShowing) BOOL showing;
@end

@implementation EGORefreshArrowView

@synthesize showing=showing;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
                
        self.clipsToBounds = YES;

        
        UIImage *image = [UIImage imageNamed:@"ft_pull_arrow.png"];
        CALayer *layer = [CALayer layer];
        layer.contentsGravity = kCAGravityCenter;
        layer.contentsScale = [[UIScreen mainScreen] scale];
        layer.contents = (id)image.CGImage;
        layer.frame = CGRectMake(floorf((self.bounds.size.width/2) - (100/2)), 0.0f, 100, self.bounds.size.height);
        [self.layer addSublayer:layer];
        _pullArrow = layer;

    }
    
    return self;
}

- (void)show:(BOOL)show animated:(BOOL)animated {
        
    [CATransaction begin];
    [CATransaction setAnimationDuration:0.2f];
    
    _pullArrow.contents = show ? (id)[UIImage imageNamed:@"ft_release_arrow.png"].CGImage : (id)[UIImage imageNamed:@"ft_pull_arrow.png"].CGImage;
    if (show) {
        _pullArrow.transform =  CATransform3DMakeRotation((M_PI/180) * 179.99999f, 0, 0, 1);
    } else {
        _pullArrow.transform = CATransform3DIdentity;
    }
    
    [CATransaction commit];
    
}

@end


@interface EGORefreshTableHeaderView (Private)
- (void)setState:(EGOPullRefreshState)aState;
@end

@implementation EGORefreshTableHeaderView

@synthesize delegate=_delegate;
@synthesize tableInset=_tableInset;

- (id)initWithFrame:(CGRect)frame {
    
    if (self = [super initWithFrame:frame]) {
        
        _patternView = [[UIView alloc] initWithFrame:self.bounds];
        [self addSubview:_patternView];
        
        self.backgroundColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
        
        UIFont *font = [UIFont boldSystemFontOfSize:12];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake((self.bounds.size.width/2), ((self.bounds.size.height-font.lineHeight)/2), 0.0f, 0.0f)];
        label.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        label.backgroundColor = self.backgroundColor;
        label.textColor = [UIColor colorWithRed:0.449f green:0.449f blue:0.449f alpha:1.0f];
        label.shadowOffset = CGSizeMake(0.0f, 1.0f);
        label.shadowColor = [UIColor colorWithWhite:1.0f alpha:0.6f];
        label.font = font;
        [_patternView insertSubview:label atIndex:1];
        _titleLabel = label;
        [label release];
		
		self.autoresizingMask = UIViewAutoresizingFlexibleWidth;
		UIActivityIndicatorView *activityView = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
        activityView.frame = CGRectMake(floorf((self.bounds.size.width/2) - 7.0f), floorf((self.bounds.size.height/2) - 7.0f), 14.0f, 14.0f);
        activityView.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin;
		[self addSubview:activityView];
		_activityView = activityView;
        [activityView release];
		
        self.tableInset = UIEdgeInsetsZero;
        _triggerOffset = -(kPullRefreshOffset+5);
		[self setState:EGOOPullRefreshNormal];
                
        
    }
    return self;	
}


#pragma mark - Setters

- (void)setWhiteStyle {
    
    //[_patternView setStyle:GiftureRefreshBumpStyleWhite];
    
}

- (void)setBlackStyle {
    
    //[_patternView setStyle:GiftureRefreshBumpStyleBlack];
    
}

- (void)setTableInset:(UIEdgeInsets)tableInset {
    _tableInset = tableInset;
    _triggerOffset = (tableInset.top + (kPullRefreshOffset+5)) * -1;
}

- (void)showActivity:(BOOL)show {
    
    return;
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
		case EGOOPullRefreshPulling:

            [_titleLabel setText:NSLocalizedString(@"Release to refresh...", nil)];
            //[_patternView setLoading:NO];

			break;
		case EGOOPullRefreshNormal:
			
             [_titleLabel setText:NSLocalizedString(@"Pull down to refresh...", nil)];
            _titleLabel.hidden = NO;
            [self showActivity:NO];
           // [_patternView setLoading:NO];	
            
			break;
		case EGOOPullRefreshLoading:
			
            [_titleLabel setText:NSLocalizedString(@"Refreshing...", nil)];
           // [_patternView setLoading:YES];

            /*
            [self showActivity:YES];
            if (!_titleLabel.hidden) {
                _titleLabel.hidden = YES;
            }*/
			
			break;
		default:
			break;
	}
	
    [_titleLabel sizeToFit];
    CGRect frame = _titleLabel.frame;
    frame.origin.x = (self.bounds.size.width-frame.size.width)/2;
    _titleLabel.frame = frame;
    //_titleLabel.frame = CGRectMake((self.bounds.size.width-_titleLabel.frame.size.width)/2, self.bounds.size.height-32.0f, _titleLabel.frame.size.width, _titleLabel.frame.size.height);
	_state = aState;
    
}

- (void)setDelegate:(id<EGORefreshTableHeaderDelegate>)delegate {
    
    _delegate = delegate;
    
    _delegateRefreshTableHeaderDidTriggerRefresh = [(id)_delegate respondsToSelector:@selector(egoRefreshTableHeaderDidTriggerRefresh:)];
    _delegateRefreshTableHeaderDidTriggerRefresh = [(id)_delegate respondsToSelector:@selector(egoRefreshTableHeaderDataSourceIsLoading:)];
    _delegateDataSourceIsEmpty = [(id)_delegate respondsToSelector:@selector(dataSourceIsEmpty)];
    
}


#pragma mark - ScrollView Methods

- (void)egoRefreshScrollViewDidScroll:(UIScrollView *)scrollView {	

    /*
    if (_backgroundView) {
        CGRect frame = _backgroundView.frame;
        
        if (scrollView.contentOffset.y < 0 && (scrollView.contentOffset.y*-1 > self.bounds.size.height)) {
            frame.origin.y = (self.bounds.size.height-(scrollView.contentOffset.y*-1));
        } else {
            frame.origin.y = 0.0f;
        }
        
        _backgroundView.frame = frame;
    }
     */
    
    
	if (_state == EGOOPullRefreshLoading) {
		
		CGFloat offset = MAX(scrollView.contentOffset.y * -1, 0);
		offset = MIN(offset, _tableInset.top + kPullRefreshOffset);
		scrollView.contentInset = UIEdgeInsetsMake(offset, 0.0f, 0.0f, 0.0f);
        
        CGRect frame = _patternView.frame;
        frame.size.height = MAX(10, ceilf((scrollView.contentOffset.y*-1)));
        frame.origin.y = ceilf(self.bounds.size.height - frame.size.height);
        _patternView.frame = frame;
        _titleLabel.alpha = (((scrollView.contentOffset.y*-1)-16)/30);
		
	} else if (scrollView.isDragging) {
		
		BOOL _loading = NO;
        if (_delegateRefreshTableHeaderDataSourceIsLoading) {
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

        CGRect frame = _patternView.frame;
        frame.size.height = MAX(10, ceilf((scrollView.contentOffset.y*-1)));
        frame.origin.y = ceilf(self.bounds.size.height - frame.size.height);
        _patternView.frame = frame;
        _titleLabel.alpha = (((scrollView.contentOffset.y*-1)-16)/30);

    }
	
}

- (void)egoRefreshScrollViewDidEndDragging:(UIScrollView *)scrollView {
    
	BOOL _loading = NO;
    if (_delegateRefreshTableHeaderDataSourceIsLoading) {
        _loading = [_delegate egoRefreshTableHeaderDataSourceIsLoading:self];
    }
    
	if (scrollView.contentOffset.y <= _triggerOffset && !_loading) {
		
        if (_delegateRefreshTableHeaderDidTriggerRefresh) {
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
    
    if (_delegateRefreshTableHeaderDataSourceIsLoading) {
        _loading = [_delegate egoRefreshTableHeaderDataSourceIsLoading:self];
    }
    if (_delegateDataSourceIsEmpty) {
        _empty = [_delegate dataSourceIsEmpty];
    }
    
    if (_loading && (_state != EGOOPullRefreshLoading) && !_empty) {
        [self setState:EGOOPullRefreshLoading];
    } else if ((_state != EGOOPullRefreshNormal) && !_loading) {// && (scrollView.contentOffset.y >= 0.0f)) {
        [self setState:EGOOPullRefreshNormal];
    }
	
}


#pragma mark - Dealloc

- (void)dealloc {
	
	_delegate=nil;
	_activityView = nil;
	_arrowView = nil;
    [super dealloc];
}


@end
