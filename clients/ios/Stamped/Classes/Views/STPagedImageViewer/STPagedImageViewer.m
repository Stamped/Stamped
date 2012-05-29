//
//  STPagedImageViewer.m
//  Stamped
//
//  Created by Devin Doty on 5/28/12.
//
//

#import "STPagedImageViewer.h"
#import "ImageLoader.h"

#define kPageViewGap 50.0f

@interface STPagedImageView : UIView {
    UIActivityIndicatorView *_activityView;
    UILabel *_errorLabel;
}
@property(nonatomic,retain) UIImageView *imageView;
@property(nonatomic,assign) NSInteger index;
@property(nonatomic,retain) NSURL *imageURL;
@property(nonatomic,readonly,getter = isLoading) BOOL loading;
@property(nonatomic,readonly,getter = isFailed) BOOL failed;
@end

@interface STPagedImageViewer ()
@end

@implementation STPagedImageViewer

@synthesize imageURLs=_imageURLs;
@synthesize scrollView=_scrollView;
@synthesize pageControl=_pageControl;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
                        
        UIScrollView *scrollView = [[UIScrollView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.bounds.size.width, self.bounds.size.height)];
        scrollView.delegate = (id<UIScrollViewDelegate>)self;
        scrollView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight | UIViewAutoresizingFlexibleBottomMargin;
        scrollView.pagingEnabled = YES;
        scrollView.showsHorizontalScrollIndicator = NO;
        scrollView.showsVerticalScrollIndicator = NO;
        scrollView.alwaysBounceHorizontal = YES;
        scrollView.alwaysBounceVertical = NO;
        [self addSubview:scrollView];
        _scrollView = [scrollView retain];
        [scrollView release];
        
        scrollView.backgroundColor = [UIColor redColor];
        
        UIPageControl *pageControl = [[UIPageControl alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height-10.0f, self.bounds.size.width, 10.0f)];
        pageControl.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin;
        [self addSubview:pageControl];
        _pageControl = [pageControl retain];
        [pageControl release];
        
    }
    return self;
}

- (void)dealloc {
    [_scrollView release], _scrollView=nil;
    [_pageControl release], _pageControl=nil;
    
    if (_imageURLs) {
        [_imageURLs release], _imageURLs=nil;
    }
    
    [super dealloc];
}

- (void)reloadData {
    
    
}


#pragma mark - Setters

- (void)setImageURLs:(NSArray *)imageURLs {
    [_imageURLs release], _imageURLs = nil;
    _imageURLs = [imageURLs retain];
    
    self.pageControl.numberOfPages = [_imageURLs count];
    [self layoutScrollView];
    [self loadScrollViewWithPage:0];
    [self loadScrollViewWithPage:1];
    
}

- (void)setViews:(NSArray*)views {
    
    NSArray *temp = _views;
    _views = [views retain];
    [temp release];
    
}


#pragma mark - Paging

- (NSInteger)currentPageIndex {
	
	CGFloat pageWidth = self.bounds.size.width;
	return ceilf((self.scrollView.contentOffset.x - pageWidth / 2) / pageWidth);
	
}

- (NSInteger)numberOfPages {
    
    return [self.imageURLs count];
    
}

- (void)moveToPage:(NSInteger)page animated:(BOOL)animated {
    if (page < 0 || page > [self numberOfPages]-1) return; // ignore out of bounds paging
	
	[self.scrollView setContentOffset:CGPointMake(page*self.scrollView.frame.size.width, 0.0f) animated:animated];
	_currentPage = page;
    _pageControl.currentPage = _currentPage;

}

- (void)pageChanged {
	
	_currentPage = [self currentPageIndex];
	_pageControl.currentPage = _currentPage;
    
	[self loadScrollViewWithPage:_currentPage+1];
	[self loadScrollViewWithPage:_currentPage-1];
    
}

- (void)layoutScrollView {
	
	if (!_views) {
		
		NSMutableArray *array = [[NSMutableArray alloc] initWithCapacity:[self numberOfPages]];
		for (NSInteger i = 0; i < [self numberOfPages]; i++) {
			[array addObject:[NSNull null]];
        }
		_views = [array retain];
		[array release];
		
	}
	
	CGSize size = CGSizeMake(self.bounds.size.width*[self numberOfPages], self.scrollView.frame.size.height);
	if (!CGSizeEqualToSize(size, self.scrollView.contentSize)) {
		self.scrollView.contentSize = size;
	}
	
	_pageControl.numberOfPages = [self numberOfPages];
	[_pageControl setCurrentPage:_currentPage];
	
}

- (void)layoutScrollViewSubviewsAnimated:(BOOL)animated {
	
	NSInteger index = [self currentPageIndex];
	
    BOOL _enabled = [UIView areAnimationsEnabled];
    [UIView setAnimationsEnabled:animated];
    [UIView beginAnimations:nil context:NULL];
    [UIView setAnimationDuration:0.5f];
    
	for (NSInteger page = index -1; page < index+3; page++) {
		
		if (page >= 0 && page < [self numberOfPages]){
			
			CGFloat originX = self.scrollView.frame.size.width * page;
			
			if (page < index) {
				originX += kPageViewGap;
			} 
			if (page > index) {
				originX -= kPageViewGap;
			}
			
			if ([_views objectAtIndex:page] == [NSNull null] || !((UIView*)[_views objectAtIndex:page]).superview){
				[self loadScrollViewWithPage:page];
			}
			
			STPagedImageView *view = (STPagedImageView*)[_views objectAtIndex:page];
			CGRect newframe = CGRectMake(originX, 0.0f, self.scrollView.bounds.size.width, self.scrollView.bounds.size.height-10.0f);
			if (!CGRectEqualToRect(view.frame, newframe)) {	
				view.frame = newframe;
			}
			
		}
	}
    
    [UIView commitAnimations];
    [UIView setAnimationsEnabled:_enabled];
	
}

- (void)prepareViewsForReuse {
	
	for (STPagedImageView *view in _views){
		if ((NSNull*)view != [NSNull null] && [view isKindOfClass:[STPagedImageView class]]) {			
			if (!(view.index == _currentPage || view.index == _currentPage-1 || view.index == _currentPage+1)) {
				if (view.superview) {
                    view.imageView.image = nil;
					[view removeFromSuperview];				
				}
				
			}
		}
	}
	
}

- (STPagedImageView*)dequeuePageView {
    
    NSArray *viewsCopy = [_views copy];
	NSInteger count = 0;
	for (STPagedImageView *view in viewsCopy){
		if ((NSNull*)view != [NSNull null] && [view isKindOfClass:[STPagedImageView class]]) {			
			if (!(view.index == _currentPage || view.index == _currentPage-1 || view.index == _currentPage+1)) {
                view.imageView.image = nil;
                view.tag = count;
                view.alpha = 1.0f;
                [viewsCopy release];
                return view;
			}
		}
		count ++;
	}	
    [viewsCopy release];
	return nil; 
	
}

- (void)loadScrollViewWithPage:(NSInteger)page {
    if (page < 0) return;
    if (page >= [_views count]) return;
    
    STPagedImageView *view = [_views objectAtIndex:page];
    if (view) {
        view = [view retain];
    }
    
    if ([view isKindOfClass:[STPagedImageView class]] && (NSNull*)view != [NSNull null] && view.superview!=nil && view.index==page) {
        return;
    }
    
    if ((NSNull*)view == [NSNull null]) {
        view = [self dequeuePageView];
        
        if (view != nil) {
            
            NSMutableArray *viewsCopy = [_views mutableCopy];
            [viewsCopy exchangeObjectAtIndex:view.tag withObjectAtIndex:page];
            [self setViews:viewsCopy];
            [viewsCopy release];
            view = [[_views objectAtIndex:page] retain];
            view.tag = -1;
            
        }
    }
    
	if (view == nil || (NSNull*)view == [NSNull null]) {
        
        view = [[STPagedImageView alloc] initWithFrame:self.bounds];
        
		NSMutableArray *viewsCopy = [_views mutableCopy];
		[viewsCopy replaceObjectAtIndex:page withObject:view];
        [self setViews:viewsCopy];
		[viewsCopy release];
		
	} 
    [view setIndex:page];
    [view setImageURL:[self.imageURLs objectAtIndex:page]];
    
    CGRect frame = CGRectMake(floorf(self.bounds.size.width * page), self.bounds.origin.y, self.bounds.size.width, self.bounds.size.height - 10.0f);
    if (page > _currentPage) {
        frame.origin.x -= 40.0f;
    } else if (page < _currentPage) {
        frame.origin.x += 40.0f;
    }
    
    if (!CGRectEqualToRect(view.frame, frame)) {
        BOOL enabled = [UIView areAnimationsEnabled];
        [UIView setAnimationsEnabled:NO];
        view.frame = frame;
        [UIView setAnimationsEnabled:enabled];
    }
    if (!view.superview) {
        [self.scrollView insertSubview:view atIndex:0];
    }

    [view release];
	
}


#pragma mark - UIScrollViewDelegate 

- (CGFloat)center {
    
    return floorf(self.scrollView.contentOffset.x + (self.scrollView.frame.size.width/2));
    
}

- (void)adjustPageAlphaAnimated:(BOOL)animated {
    return;
    
    BOOL _enabled = [UIView areAnimationsEnabled];
    [UIView setAnimationsEnabled:animated];
    [UIView beginAnimations:nil context:NULL];
    [UIView setAnimationDuration:0.1f];
    
    CGRect rect = CGRectMake(self.scrollView.contentOffset.x, 0.0f, self.bounds.size.width, self.bounds.size.height);
    NSInteger index = [self currentPageIndex];
    for (NSInteger page = index -1; page < index+3; page++) {
		
		if (page >= 0 && page < [self numberOfPages]){
			
            STPagedImageView *view = (STPagedImageView*)[_views objectAtIndex:page];
            if (view && [view isKindOfClass:[UIView class]]) {
                
                CGRect intersection = CGRectIntersection(rect, view.frame);
                CGFloat diff = intersection.size.width / 200.0f;
                view.alpha = diff;
                
            }
		}
	}
    
    [UIView commitAnimations];
    [UIView setAnimationsEnabled:_enabled];

}

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
    
    NSInteger page = [self currentPageIndex];
    page = MAX(0, page);
    page = MIN(page, [self numberOfPages]-1);
    
    if (_currentPage != page) {
        
        _currentPage = page;
		_pageControl.currentPage = page;
        
        if (!scrollView.tracking && !scrollView.dragging) {
            [self layoutScrollViewSubviewsAnimated:NO];
        }

	}
    
    [self adjustPageAlphaAnimated:NO];

}

- (void)scrollViewDidEndDragging:(UIScrollView *)scrollView willDecelerate:(BOOL)decelerate {
    
	[self layoutScrollViewSubviewsAnimated:YES];
    [self adjustPageAlphaAnimated:YES];
    
}

- (void)scrollViewDidEndDecelerating:(UIScrollView *)scrollView {
	
	if (_currentPage != [self currentPageIndex]) {
        [self pageChanged];
        [self moveToPage:[self currentPageIndex] animated:YES];
	}
    
    [self adjustPageAlphaAnimated:NO];
	[self layoutScrollViewSubviewsAnimated:NO];

}


@end



#pragma mark - STPagedImageView

@implementation STPagedImageView
@synthesize index;
@synthesize imageURL=_imageURL;
@synthesize imageView=_imageView;
@synthesize loading=_loading;
@synthesize failed=_failed;

- (id)initWithFrame:(CGRect)frame {
    
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor clearColor];
            
        UIImageView *imageView = [[UIImageView alloc] initWithFrame:CGRectZero];
        imageView.contentMode = UIViewContentModeScaleAspectFit;
        [self addSubview:imageView];
        self.imageView = imageView;
        [imageView release];
    
        imageView.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
        imageView.layer.shadowOpacity = 0.2f;
        imageView.layer.shadowRadius = 6.0f;
        
    }
    return self;
    
}

- (void)setLoading:(BOOL)loading {
    _loading = loading;
    
    _imageView.hidden = _loading;
    
    if (_loading) {
        
        if (!_activityView) {
            
            UIActivityIndicatorView *view = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
            view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
            [self addSubview:view];
            [view release];

            _activityView = view;
            [_activityView startAnimating];
            _activityView.frame = CGRectMake((self.bounds.size.width-20.0f)/2, (self.bounds.size.height-20.0f)/2, 20.0f, 20.0f);
            
        }
        
    } else {
        
        if (_activityView) {
            [_activityView removeFromSuperview], _activityView=nil;
        }
        
    }
    
}

- (void)setFailed:(BOOL)failed {
    _failed = failed;
    
    self.imageView.hidden = failed;
    
    if (_failed) {
        
        if (!_errorLabel) {
            
            UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
            label.font = [UIFont boldSystemFontOfSize:12];
            label.textColor = [UIColor darkGrayColor];
            label.backgroundColor = [UIColor clearColor];
            [self addSubview:label];
            _errorLabel = label;
            [label release];
            
            label.text = @"Failed to load.";
            [label sizeToFit];
            CGRect frame = label.frame;
            frame.origin.x = (self.bounds.size.width - frame.size.width);
            frame.origin.y = (self.bounds.size.height - frame.size.height);
            label.frame = frame;
            
        }
        
    } else {
        
        if (_errorLabel) {
            [_errorLabel removeFromSuperview], _errorLabel=nil;
        }
        
    }
    
}

- (void)dealloc {
    
    [[ImageLoader sharedLoader] cancelRequestForURL:_imageURL];
    [_imageURL release], _imageURL=nil;
    [super dealloc];
    
}

- (void)layoutSubviews {
    [super layoutSubviews];
}

- (void)setImageURL:(NSURL *)imageURL {
    if (_imageURL && [_imageURL isEqual:imageURL]) return; // already loading or set
    
    self.failed = NO;
    self.loading = NO;
    
    if (!self.imageView.image) {
        [[ImageLoader sharedLoader] cancelRequestForURL:_imageURL];
    }

    [_imageURL release], _imageURL=nil;
    _imageURL = [imageURL retain];
    
    [[ImageLoader sharedLoader] imageForURL:_imageURL completion:^(UIImage *image, NSURL *url) {
        if ([_imageURL isEqual:url]) {
            self.loading = NO;
            self.failed = (image == nil);
            
            if (image) {
                
                CGFloat heightFactor = image.size.height / (self.frame.size.height-20.0f);
                CGFloat widthFactor = image.size.width / (self.frame.size.width-60.0f);
                
                CGFloat scaleFactor = MAX(heightFactor, widthFactor);
                
                CGFloat newHeight = image.size.height / scaleFactor;
                CGFloat newWidth = image.size.width / scaleFactor;
                
                CGRect rect = CGRectMake((self.frame.size.width - newWidth)/2, (self.frame.size.height-newHeight)/2, newWidth, newHeight);
                self.imageView.frame = rect;
                self.imageView.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.imageView.bounds].CGPath;
                self.imageView.image = image;

            }
            
        }
    }];
    
}



@end
