//
//  STPagedImageViewer.m
//  Stamped
//
//  Created by Devin Doty on 5/28/12.
//
//

#import "STPagedImageViewer.h"
#import "ImageLoader.h"

@interface STPagedImageView : UIView
@property(nonatomic,retain) UIImageView *imageView;
@property(nonatomic,assign) NSInteger index;
@property(nonatomic,retain) NSURL *imageURL;
@end

@interface STPagedImageViewer ()
@end

@implementation STPagedImageViewer

@synthesize imageURLs=_imageURLs;
@synthesize scrollView=_scrollView;
@synthesize pageControl=_pageControl;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        _views = [[NSMutableArray alloc] init];
        
        UIScrollView *scrollView = [[UIScrollView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.bounds.size.width, self.bounds.size.height-10.0f)];
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

- (STPagedImageView*)dequeueGridView {
    
    NSArray *viewsCopy = [_views copy];
	NSInteger count = 0;
	for (STPagedImageView *view in viewsCopy){
		if ((NSNull*)view != [NSNull null] && [view isKindOfClass:[STPagedImageView class]]) {			
			if (!(view.index == _currentPage || view.index == _currentPage-1 || view.index == _currentPage+1)) {
                view.imageView.image = nil;
                view.tag = count;
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
        view = [self dequeueGridView];
        
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
    
    CGRect frame = CGRectMake(floorf(self.bounds.size.width * page), self.bounds.origin.y, self.bounds.size.width, self.bounds.size.height);
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

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
    
    NSInteger page = [self currentPageIndex];
    page = MAX(0, page);
    page = MIN(page, [self numberOfPages]-1);
    
	if (_currentPage != page) {
        
        scrollView.bounces = (page != 0);
		_pageControl.currentPage = page;
        
        STPagedImageView *view = [_views objectAtIndex:page];
        if (((NSNull*)view == [NSNull null]) || ([view isKindOfClass:[STPagedImageView class]] && !view.superview)) {
            [self loadScrollViewWithPage:page];
        }
        
	}
    
}

- (void)scrollViewDidEndDecelerating:(UIScrollView *)scrollView{
	
	if (_currentPage != [self currentPageIndex]) {
        [self pageChanged];
	}
	
}

@end



#pragma mark - STPagedImageView

@implementation STPagedImageView
@synthesize index;
@synthesize imageURL=_imageURL;
@synthesize imageView;

- (void)dealloc {
    [_imageURL release], _imageURL=nil;
    [super dealloc];
}

- (void)setImageURL:(NSURL *)imageURL {
    if (_imageURL && [_imageURL isEqual:imageURL]) return; // already loading or set
    
    [_imageURL release], _imageURL=nil;
    _imageURL = [imageURL retain];
    
    [[ImageLoader sharedLoader] imageForURL:_imageURL completion:^(UIImage *image, NSURL *url) {
        
    }];
    
    
}



@end
