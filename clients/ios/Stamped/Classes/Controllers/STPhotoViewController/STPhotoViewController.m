//
//  GifturePhotoViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/25/12.
//
//

#import "ImageLoader.h"

#define kSTZoomViewTag 0x101
#define kSTPVZoomScale 2.5
#define kBackgroundColor [UIColor colorWithRed:0.8980f green:0.8980f blue:0.8980f alpha:1.0f]

@interface STPhotoLoadingView : UIView {
@private
    CGFloat _progress;
}
@end

@interface STPhotoScrollView : UIScrollView
@end

@interface STPhotoView : UIView {
    BOOL _ignoreScroll;
    CGFloat _beginRadians;
    STPhotoLoadingView *_loadingView;
    UILabel *_titleLabel;
    CGSize _imageSize;
    BOOL _cancelled;
    
    NSURLConnection *_connection;
    NSMutableData *_responseData;
    NSDictionary *_response;

}
@property(nonatomic,retain) UIImageView *imageView;
@property(nonatomic,retain) STPhotoScrollView *scrollView;

- (void)setImageURL:(NSURL*)aURL;
- (void)setTitle:(NSString*)title;
- (void)cancel;
@end


#import "STPhotoViewController.h"

@implementation STPhotoViewController

@synthesize photoTitle;

- (id)initWithURL:(NSURL*)aURL {
    
    if ((self = [super init])) {
        _URL = [aURL retain];
    }
    return self;
    
}


#pragma mark - View lifecycle

- (void)loadView {

    CGRect appFrame = [[UIScreen mainScreen] applicationFrame];
    appFrame.origin.y += 44.0f;
    appFrame.size.height -= 44.0f;
    STPhotoView *view = [[STPhotoView alloc] initWithFrame:appFrame];    
    view.backgroundColor = kBackgroundColor;
    [view setImageURL:_URL];
    self.view = view;
    [view release];
        
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
}

- (void)viewDidUnload {
    [super viewDidUnload];
}

- (void)dealloc {
    [_URL release], _URL=nil;
    [(STPhotoView*)self.view cancel];
    [super dealloc];
}


#pragma mark - Setters

- (void)setPhotoTitle:(NSString *)aPhotoTitle {
    
    [(STPhotoView*)self.view setTitle:aPhotoTitle];
    
}

@end


#pragma mark - STPhotoLoadingView

@implementation STPhotoLoadingView

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        self.backgroundColor = kBackgroundColor;
    }
    return self;
    
}

- (void)setProgress:(CGFloat)progress {
    
    _progress = MIN(progress, 1.0f);
    _progress = MAX(0.0f, _progress);

    [self setNeedsDisplay];
    
}

- (void)drawRect:(CGRect)rect {
    
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGPathRef _path = [UIBezierPath bezierPathWithRoundedRect:CGRectInset(rect, 4, 4) cornerRadius:6].CGPath;
    
    [[UIColor colorWithRed:0.502f green:0.502f blue:0.502f alpha:1.0f] setFill];
    [[UIColor colorWithRed:0.502f green:0.502f blue:0.502f alpha:1.0f] setStroke];
    
    CGContextSetLineWidth(ctx, 2);
    CGContextAddPath(ctx, _path);
    CGContextStrokePath(ctx);
    
    CGFloat width = rect.size.width;
    rect.size.width = width*_progress;
    _path = [UIBezierPath bezierPathWithRoundedRect:CGRectInset(rect, 4, 4) cornerRadius:6].CGPath;
    CGContextAddPath(ctx, _path);
    CGContextFillPath(ctx);
    
}

@end


#pragma mark - STPhotoScrollView

@implementation STPhotoScrollView

- (id)initWithFrame:(CGRect)frame {
    
    if ((self = [super initWithFrame:frame])) {
        
        self.scrollEnabled = YES;
		self.pagingEnabled = NO;
		self.clipsToBounds = NO;
		self.maximumZoomScale = 3.0f;
		self.minimumZoomScale = 1.0f;
		self.showsVerticalScrollIndicator = NO;
		self.showsHorizontalScrollIndicator = NO;
		self.alwaysBounceVertical = NO;
		self.alwaysBounceHorizontal = NO;
		self.bouncesZoom = YES;
		self.bounces = YES;
		self.scrollsToTop = NO;
		self.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
		self.decelerationRate = UIScrollViewDecelerationRateFast;
        
    }
    
    return self;
    
}

- (void)zoomRectWithCenter:(CGPoint)center {
	
	CGRect rect;
	rect.size = CGSizeMake(self.frame.size.width / kSTPVZoomScale, self.frame.size.height / kSTPVZoomScale);
	rect.origin.x = MAX((center.x - (rect.size.width / 2.0f)), 0.0f);		
	rect.origin.y = MAX((center.y - (rect.size.height / 2.0f)), 0.0f);
	
	CGRect frame = [self.superview convertRect:self.frame toView:self.superview];
	CGFloat borderX = frame.origin.x;
	CGFloat borderY = frame.origin.y;
	
	if (borderX > 0.0f && (center.x < borderX || center.x > self.frame.size.width - borderX)) {
        
		if (center.x < (self.frame.size.width / 2.0f)) {
			
			rect.origin.x += (borderX/kSTPVZoomScale);
			
		} else {
			
			rect.origin.x -= ((borderX/kSTPVZoomScale) + rect.size.width);
			
		}	
	}
	
	if (borderY > 0.0f && (center.y < borderY || center.y > self.frame.size.height - borderY)) {
        
		if (center.y < (self.frame.size.height / 2.0f)) {
			
			rect.origin.y += (borderY/kSTPVZoomScale);
			
		} else {
            
			rect.origin.y -= ((borderY/kSTPVZoomScale) + rect.size.height);
			
		}
		
	}
    
	[self zoomToRect:rect animated:YES];	
    
}

@end


#pragma mark - STPhotoView

@interface STPhotoView ()
@end


@implementation STPhotoView

@synthesize scrollView=_scrollView;
@synthesize imageView=_imageView;

- (id)initWithFrame:(CGRect)frame {
    
    if ((self = [super initWithFrame:frame])) {
                
        self.backgroundColor = kBackgroundColor;
		self.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
		self.opaque = YES;
		
		STPhotoScrollView *scrollView = [[STPhotoScrollView alloc] initWithFrame:self.bounds];
        scrollView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
		scrollView.backgroundColor = kBackgroundColor;
		scrollView.opaque = YES;
		scrollView.delegate = (id<UIScrollViewDelegate>)self;
		[self addSubview:scrollView];
		_scrollView = scrollView;
        [scrollView release];
            
		UIImageView *imageView = [[UIImageView alloc] initWithFrame:self.bounds];
        imageView.backgroundColor = kBackgroundColor;
		imageView.opaque = YES;
		imageView.contentMode = UIViewContentModeScaleAspectFit;
		imageView.tag = kSTZoomViewTag;
		[_scrollView addSubview:imageView];
		_imageView = imageView;
        [imageView release];
        
        UIRotationGestureRecognizer *gesture = [[UIRotationGestureRecognizer alloc] initWithTarget:self action:@selector(rotate:)];
        gesture.delegate = (id<UIGestureRecognizerDelegate>)self;
		[self addGestureRecognizer:gesture];
        [gesture release];
        
        UITapGestureRecognizer *tap = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(doubleTap:)];
        tap.numberOfTapsRequired = 2;
        [self addGestureRecognizer:tap];
        [tap release];
        
        _imageSize = CGSizeZero;

        self.userInteractionEnabled = NO;
        
    }
    
    return self;
    
}

- (void)dealloc {
    if (_connection) {
        [_connection cancel];
        [_connection release], _connection=nil;
    }
    if (_responseData) {
        [_responseData release], _responseData=nil;
    }
    if (_response) {
        [_response release], _response=nil;
    }
    _scrollView=nil;
    _imageView=nil;
    _titleLabel=nil;
    [super dealloc];
}


#pragma mark - Setters

- (void)setTitle:(NSString*)title {
    
    if (!_titleLabel) {
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(10, self.bounds.size.height - 200, self.bounds.size.width - 20, 20)];
        label.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        label.textColor = [UIColor colorWithRed:0.522f green:0.549f blue:0.580f alpha:1.0f];
        label.shadowColor = [UIColor whiteColor];
        label.shadowOffset = CGSizeMake(0, 1);
        label.textAlignment = UITextAlignmentCenter;
        label.backgroundColor = kBackgroundColor;
        label.font = [UIFont boldSystemFontOfSize:14];
        [self addSubview:label];
        _titleLabel=label;
        [label release];
    }
    
    _titleLabel.text = title;
    
}

- (void)setLoading:(BOOL)loading percentComplete:(CGFloat)complete {
    
    if (loading) {
        
        if (_loadingView==nil) {
            STPhotoLoadingView *view = [[STPhotoLoadingView alloc] initWithFrame:CGRectMake(50, floorf(self.bounds.size.height/2), self.bounds.size.width-100, 16)];
            view.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
            [self addSubview:view];
            _loadingView=view;
        }
        
        [_loadingView setProgress:complete];
        
    } else {
        
        if (_loadingView!=nil) {
            [_loadingView removeFromSuperview];
            _loadingView=nil;
        }
        
    }
    
}

- (void)setImageURL:(NSURL*)aURL {
    [self setLoading:YES percentComplete:0];
    
    if (_responseData) {
        [_responseData release], _responseData=nil;
    }
    _responseData = [[NSMutableData alloc] init];

    NSURLRequest *request = [[NSURLRequest alloc] initWithURL:aURL];
    NSURLConnection *connection = [[NSURLConnection alloc] initWithRequest:request delegate:(id<NSURLConnectionDataDelegate>)self];
    [connection start];
    _connection = [connection retain];
    [request release];
    [connection release];
}


#pragma mark - State

- (void)finished {
    if (!_responseData) return;
    
    __block UIImage *image = [[UIImage alloc] initWithData:_responseData];
    [_responseData release], _responseData=nil;

    _imageSize = image.size;
    _imageView.image = image;
    [self layoutScrollViewAnimated:NO];
    [image release];
    
    __block UIView *view = _imageView;
    view.alpha = 0.0f;
    view.transform = CGAffineTransformMakeScale(0.98f, 0.98f);
    
    if (_titleLabel) {
        
        [UIView animateWithDuration:.35f delay:.2 options:UIViewAnimationCurveEaseOut animations:^{
            
            if (_titleLabel) {
                CGRect frame = _titleLabel.frame;
                frame.origin.y  = CGRectGetMaxY(view.frame) + 10;
                _titleLabel.frame = frame;
            }
            
        } completion:^(BOOL finished) {
            
            [self setLoading:NO percentComplete:0];
            
        }];
        
    } else {
        
        dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 0.2f * NSEC_PER_SEC), dispatch_get_main_queue(), ^(void){
            [self setLoading:NO percentComplete:0];
        });
        
    }
    
    [UIView animateWithDuration:0.3f delay:0.2f options:UIViewAnimationCurveEaseOut animations:^{
        
        view.alpha = 1.0f;
        view.transform = CGAffineTransformMakeScale(1.0f, 1.0f);
        
    } completion:^(BOOL finished){
        
        self.userInteractionEnabled = YES;
        [self layoutScrollViewAnimated:NO];
        view.layer.shadowOpacity = 0.4f;
        view.layer.shadowOffset = CGSizeMake(0.0f, 0.0f);
        view.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.imageView.bounds].CGPath;
        
        if (_titleLabel) {
            [self insertSubview:_titleLabel atIndex:0]; // move to the bottom
        }
        
        
    }];
    
}

- (void)cancel {
    
    if (!_cancelled && _connection) {
        [_connection cancel];
        _cancelled = YES;
    }
    
}


#pragma mark - Layout

- (CGRect)frameToFitCurrentView {
	
	CGFloat heightFactor = _imageSize.height / self.frame.size.height;
	CGFloat widthFactor = _imageSize.width / self.frame.size.width;
	
	CGFloat scaleFactor = MAX(heightFactor, widthFactor);
	
	CGFloat newHeight = _imageSize.height / scaleFactor;
	CGFloat newWidth = _imageSize.width / scaleFactor;
	
	CGRect rect = CGRectMake((self.frame.size.width - newWidth)/2, (self.frame.size.height-newHeight)/2, newWidth, newHeight);
	
	return rect;
	
}

- (void)centerImageView {

    if (_ignoreScroll) {
        return;
    }
    
    self.imageView.layer.position = CGPointMake(self.scrollView.bounds.size.width/2, self.scrollView.bounds.size.height/2);

}

- (void)layoutScrollViewAnimated:(BOOL)animated {

	if (animated) {
		[UIView beginAnimations:nil context:NULL];
		[UIView setAnimationDuration:0.0001];
	}

    self.scrollView.frame = [self frameToFitCurrentView];   
	self.scrollView.contentSize = self.scrollView.bounds.size;
	self.scrollView.contentOffset = CGPointMake(0.0f, 0.0f);
    
	self.imageView.frame = self.scrollView.bounds;
    self.imageView.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.imageView.bounds].CGPath;

	if (animated) {
		[UIView commitAnimations];
	}
    
}


#pragma mark - UIScrollViewDelegate

- (void)scrollViewDidZoom:(UIScrollView *)scrollView {
    
    [self centerImageView];
    
}

- (UIView *)viewForZoomingInScrollView:(UIScrollView *)scrollView {
	return [_scrollView viewWithTag:kSTZoomViewTag];
}

- (void)scrollViewDidEndZooming:(UIScrollView *)scrollView withView:(UIView *)view atScale:(float)scale {
    
    return;
	if (scrollView.zoomScale > 1.0f) {		
		
		
		CGFloat height, width, originX, originY;
		height = MIN(CGRectGetHeight(self.imageView.frame) + self.imageView.frame.origin.x, CGRectGetHeight(self.bounds));
		width = MIN(CGRectGetWidth(self.imageView.frame) + self.imageView.frame.origin.y, CGRectGetWidth(self.bounds));
        
		
		if (CGRectGetMaxX(self.imageView.frame) > self.bounds.size.width) {
			width = CGRectGetWidth(self.bounds);
			originX = 0.0f;
		} else {
			width = CGRectGetMaxX(self.imageView.frame);
			
			if (self.imageView.frame.origin.x < 0.0f) {
				originX = 0.0f;
			} else {
				originX = self.imageView.frame.origin.x;
			}	
		}
		
		if (CGRectGetMaxY(self.imageView.frame) > self.bounds.size.height) {
			height = CGRectGetHeight(self.bounds);
			originY = 0.0f;
		} else {
			height = CGRectGetMaxY(self.imageView.frame);
			
			if (self.imageView.frame.origin.y < 0.0f) {
				originY = 0.0f;
			} else {
				originY = self.imageView.frame.origin.y;
			}
		}
        
		CGRect frame = self.scrollView.frame;
		self.scrollView.frame = CGRectMake((self.bounds.size.width / 2) - (width / 2), (self.bounds.size.height / 2) - (height / 2), width, height);
		self.scrollView.layer.position = CGPointMake(self.bounds.size.width/2, self.bounds.size.height/2);
		if (!CGRectEqualToRect(frame, self.scrollView.frame)) {		
			
			CGFloat offsetY, offsetX;
            
			if (frame.origin.y < self.scrollView.frame.origin.y) {
				offsetY = self.scrollView.contentOffset.y - (self.scrollView.frame.origin.y - frame.origin.y);
			} else {				
				offsetY = self.scrollView.contentOffset.y - (frame.origin.y - self.scrollView.frame.origin.y);
			}
			
			if (frame.origin.x < self.scrollView.frame.origin.x) {
				offsetX = self.scrollView.contentOffset.x - (self.scrollView.frame.origin.x - frame.origin.x);
			} else {				
				offsetX = self.scrollView.contentOffset.x - (frame.origin.x - self.scrollView.frame.origin.x);
			}
            
			if (offsetY < 0) offsetY = 0;
			if (offsetX < 0) offsetX = 0;
			
			self.scrollView.contentOffset = CGPointMake(offsetX, offsetY);
		}
        
        self.imageView.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.imageView.bounds].CGPath;
        
	} else {
        
		[self layoutScrollViewAnimated:YES];
        
	}
}	

- (void)killScrollViewZoom {

    [UIView animateWithDuration:.3 animations:^{
        CGFloat hfactor = self.imageView.image.size.width / self.frame.size.width;
        CGFloat vfactor = self.imageView.image.size.height / self.frame.size.height;
        
        CGFloat factor = MAX(hfactor, vfactor);
        
        CGFloat newWidth = self.imageView.image.size.width / factor;
        CGFloat newHeight = self.imageView.image.size.height / factor;
        
        CGFloat leftOffset = (self.frame.size.width - newWidth) / 2;
        CGFloat topOffset = (self.frame.size.height - newHeight) / 2;
        
        self.scrollView.frame = CGRectMake(leftOffset, topOffset, newWidth, newHeight);
        self.imageView.frame = self.scrollView.bounds;
        
    } completion:^(BOOL finished) {
        
        [_scrollView setZoomScale:1.0f animated:NO];
		_imageView.frame = _scrollView.bounds;
		[self layoutScrollViewAnimated:NO];
        
    }];

}


#pragma mark - Gestures

- (BOOL)gestureRecognizer:(UIGestureRecognizer *)gestureRecognizer shouldRecognizeSimultaneouslyWithGestureRecognizer:(UIGestureRecognizer *)otherGestureRecognizer {
    return YES;
}

- (void)rotate:(UIRotationGestureRecognizer*)gesture {
    
	if (gesture.state == UIGestureRecognizerStateBegan) {
		
        if (_titleLabel) {
            _titleLabel.alpha = 0;
        }
        
		_beginRadians = gesture.rotation;
		self.scrollView.layer.transform = CATransform3DMakeRotation(_beginRadians, 0.0f, 0.0f, 1.0f);
		
	} else if (gesture.state == UIGestureRecognizerStateChanged) {
		
		self.scrollView.layer.transform = CATransform3DMakeRotation((_beginRadians + gesture.rotation), 0.0f, 0.0f, 1.0f);
        
	} else {
        
        [UIView animateWithDuration:0.3f animations:^{
            self.scrollView.layer.transform = CATransform3DIdentity;
            
            if (_titleLabel) {
                _titleLabel.alpha = 1;
            }
            
        } completion:^(BOOL finished) {
            self.scrollView.frame = [self frameToFitCurrentView]; 
            
        }];
        

	} 
    
}

- (void)doubleTap:(UITapGestureRecognizer*)gesture {
    
    if (self.scrollView.zoomScale > 1) {
        [self killScrollViewZoom];
    } else {
        _ignoreScroll = YES;
        [self.scrollView zoomRectWithCenter:[gesture locationInView:self.scrollView]];
        _ignoreScroll = NO;
    }
    
}


#pragma mark - NSURLConnectionDelegate

- (NSDictionary*)responseHeaders {
	if(_response && [_response isKindOfClass:[NSHTTPURLResponse class]]) {
		return [(NSHTTPURLResponse*)_response allHeaderFields];
	} else {
		return nil;	
	}
}

- (void)connection:(NSURLConnection *)connection didReceiveData:(NSData *)data {
	if(connection != _connection || _cancelled) return;
	[_responseData appendData:data];   
    
    if (([[self responseHeaders] objectForKey:@"Content-Length"] !=nil)) {
        CGFloat length = [[[self responseHeaders] objectForKey:@"Content-Length"] floatValue];
        if (!_cancelled) {
            [self setLoading:YES percentComplete:([_responseData length]/length)];
        }
    }
    
}

- (void)connection:(NSURLConnection *)connection didReceiveResponse:(NSURLResponse *)response {
	if(connection != _connection) return;
	_response = (id)[response retain];
}

- (void)connectionDidFinishLoading:(NSURLConnection *)connection {
    
    dispatch_async(dispatch_get_main_queue(), ^{
        [self finished];
    });
    
}

- (void)connection:(NSURLConnection *)connection didFailWithError:(NSError *)error {
    
    dispatch_async(dispatch_get_main_queue(), ^{
        if (error) {
            [self setTitle:[error localizedDescription]];
        } else {
            [self setTitle:@"Image not found."];
        }
        [self setLoading:NO percentComplete:0];
    });
    
}

@end



