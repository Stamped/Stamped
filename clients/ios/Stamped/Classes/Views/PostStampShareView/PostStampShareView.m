//
//  PostStampShareView.m
//  Stamped
//
//  Created by Devin Doty on 6/18/12.
//
//

#import "PostStampShareView.h"
#import "Util.h"
#import "STBlockUIView.h"
#import "QuartzUtils.h"

@interface PostStampShareCell : UIControl
@property(nonatomic,retain) UILabel *titleLabel;
@property(nonatomic,retain) UIImageView *imageView;
@property(nonatomic,retain) UIImageView *accessoryImageView;
@property(nonatomic,retain) UIView *highlightView;
@property(nonatomic,assign) BOOL shared;
@property(nonatomic,assign) BOOL loading;
@property(nonatomic,retain) UIActivityIndicatorView *activityView;
@property(nonatomic,assign) UIRectCorner corners;
@end

@interface PostStampShareView ()
@property(nonatomic,retain) UIImageView *contentView;
@end

@implementation PostStampShareView
@synthesize contentView;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
    
        UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tapped:)];
        gesture.delegate = (id<UIGestureRecognizerDelegate>)self;
        [self addGestureRecognizer:gesture];
        [gesture release];

        UIImage *image = [UIImage imageNamed:@"post_stamp_share_popover.png"];
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleWidth;
        imageView.userInteractionEnabled = YES;
        [self addSubview:imageView];
        self.contentView = imageView;
        [imageView release];
        
        CGRect frame = imageView.frame;
        frame.size.height = image.size.height;
        frame.size.width = self.bounds.size.width;
        frame.origin.y = (self.bounds.size.height-image.size.height)/2;
        imageView.frame = frame;
    
        CGFloat width = 294.0f;
        PostStampShareCell *cell = [[PostStampShareCell alloc] initWithFrame:CGRectMake((imageView.bounds.size.width-width)/2, 9.0f, width, 48.0f)];
        cell.corners = (UIRectCornerTopLeft | UIRectCornerTopRight);
        cell.titleLabel.text = @"Share on Facebook";
        cell.imageView.image = [UIImage imageNamed:@"post_stamp_facebook_icon.png"];
        [cell addTarget:self action:@selector(facebook:) forControlEvents:UIControlEventTouchUpInside];
        [imageView addSubview:cell];
        [cell release];
        
        UIView *border = [[UIView alloc] initWithFrame:CGRectMake((imageView.bounds.size.width-width)/2, CGRectGetMaxY(cell.frame), width, 1.0f)];
        border.backgroundColor = [UIColor colorWithWhite:0.0f alpha:0.1f];
        border.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        [imageView addSubview:border];
        [border release];
        
        cell = [[PostStampShareCell alloc] initWithFrame:CGRectMake((imageView.bounds.size.width-width)/2, CGRectGetMaxY(cell.frame)+2.0f, width, 48.0f)];
        cell.corners = (UIRectCornerBottomLeft | UIRectCornerBottomRight);
        cell.titleLabel.text = @"Share on Twitter";
        cell.imageView.image = [UIImage imageNamed:@"post_stamp_twitter_icon.png"];
        [cell addTarget:self action:@selector(twitter:) forControlEvents:UIControlEventTouchUpInside];
        [imageView addSubview:cell];
        [cell release];
                
    }
    return self;
}

- (void)dealloc {
    self.contentView = nil;
    [super dealloc];
}

- (void)popIn {
    
    CAKeyframeAnimation *scale = [CAKeyframeAnimation animationWithKeyPath:@"transform.scale"];
    scale.duration = 0.45f;
    scale.values = [NSArray arrayWithObjects:[NSNumber numberWithFloat:.7f], [NSNumber numberWithFloat:1.1f], [NSNumber numberWithFloat:.9f], [NSNumber numberWithFloat:1.f], nil];
    
    CABasicAnimation *opacity = [CABasicAnimation animationWithKeyPath:@"opacity"];
    opacity.duration = 0.45f * .4f;
    opacity.fromValue = [NSNumber numberWithFloat:0.f];
    opacity.toValue = [NSNumber numberWithFloat:1.f];
    opacity.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseOut];
    opacity.fillMode = kCAFillModeForwards;
    
    CAAnimationGroup *animation = [CAAnimationGroup animation];
    [animation setAnimations:[NSArray arrayWithObjects:scale, opacity, nil]];
    animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
    [self.contentView.layer addAnimation:animation forKey:nil];
    
}


#pragma mark - Actions

- (void)facebook:(PostStampShareCell*)sender {
    
    [Util warnWithMessage:@"Not implemented yet" andBlock:nil];
    /*
    sender.loading = YES;
    
    double delayInSeconds = 2.0;
    dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, delayInSeconds * NSEC_PER_SEC);
    dispatch_after(popTime, dispatch_get_main_queue(), ^(void){
        
        sender.loading = NO;
        sender.titleLabel.text = @"Shared on Facebook";
        sender.shared = YES;
        
        
    });
     */
}

- (void)twitter:(PostStampShareCell*)sender {
    [Util warnWithMessage:@"Not implemented yet" andBlock:nil];
    /*
    sender.loading = YES;
    
    double delayInSeconds = 2.0;
    dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, delayInSeconds * NSEC_PER_SEC);
    dispatch_after(popTime, dispatch_get_main_queue(), ^(void){

        sender.loading = NO;
        sender.titleLabel.text = @"Shared on Twitter";
        sender.shared = YES;

    });    
     */
}


#pragma mark - Gestures

- (void)tapped:(UITapGestureRecognizer*)gesture {
    
    [UIView animateWithDuration:0.25f animations:^{
        self.alpha = 0.0f;
    } completion:^(BOOL finished) {
        [self removeFromSuperview];
    }];
    
}


#pragma mark - UIGestureRecognizerDelegate

- (BOOL)gestureRecognizerShouldBegin:(UIGestureRecognizer *)gestureRecognizer {
    
    CGPoint point = [gestureRecognizer locationInView:self];
    return !CGRectContainsPoint(self.contentView.frame, point);
    
}



@end


#pragma mark - PostStampShareCell

@implementation PostStampShareCell
@synthesize titleLabel=_titleLabel;
@synthesize imageView=_imageView;
@synthesize accessoryImageView=_accessoryImageView;
@synthesize shared=_shared;
@synthesize highlightView;
@synthesize corners;
@synthesize activityView;
@synthesize loading=_loading;

- (id)initWithFrame:(CGRect)frame {
    
    if (self = [super initWithFrame:frame]) {
        
        self.backgroundColor = [UIColor clearColor];
        
        UIFont *font = [UIFont boldSystemFontOfSize:14];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(50.0f, floorf((self.bounds.size.height-font.lineHeight)/2), 0.0f, font.lineHeight)];
        label.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleLeftMargin;
        label.textColor = [UIColor colorWithWhite:0.349f alpha:1.0f];
        label.highlightedTextColor = [UIColor whiteColor];
        label.font = font;
        label.backgroundColor = [UIColor clearColor];
        label.lineBreakMode = UILineBreakModeTailTruncation;
        [self addSubview:label];
        self.titleLabel = label;
        [label release];
        
        UIImageView *imageView = [[UIImageView alloc] initWithFrame:CGRectMake(10.0f, (self.bounds.size.height-28.0f)/2, 28.0f, 28.0f)];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
        [self addSubview:imageView];
        self.imageView = imageView;
        [imageView release];
        
        imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"post_stamp_share_check.png"]];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleLeftMargin;
        [self addSubview:imageView];
        self.accessoryImageView = imageView;
        [imageView release];
        imageView.hidden = YES;
        
        CGRect frame = imageView.frame;
        frame.origin.x = (self.bounds.size.width-32.0f);
        frame.origin.y = (self.bounds.size.height-frame.size.height)/2;
        imageView.frame = frame;
        
    }
    return self;
    
}

- (void)dealloc {
    self.imageView = nil;
    self.titleLabel = nil;
    self.accessoryImageView = nil;
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    [self.titleLabel sizeToFit];
}


#pragma mark - Setters

- (void)setHighlighted:(BOOL)highlighted {
    [super setHighlighted:highlighted];
    
    self.titleLabel.highlighted = highlighted;
    
    if (highlighted) {
        
        if (!highlightView) {
            
            STBlockUIView *view = [[STBlockUIView alloc] initWithFrame:self.bounds];
            view.backgroundColor = [UIColor clearColor];
            [self insertSubview:view atIndex:0];
            highlightView = view;
            [view setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
               
                CGPathRef path = [UIBezierPath bezierPathWithRoundedRect:rect byRoundingCorners:self.corners cornerRadii:CGSizeMake(2.0f, 2.0f)].CGPath;
                CGContextAddPath(ctx, path);
                CGContextClip(ctx);
                
                UIColor *topColor = [UIColor colorWithRed:0.019f green:0.545f blue:0.96f alpha:1.0f];
                UIColor *bottomColor = [UIColor colorWithRed:0.0039f green:0.364f blue:0.901f alpha:1.0f];
                drawGradient(topColor.CGColor, bottomColor.CGColor, ctx);
                
                
            }];
            [view release];
            
        }
        
    } else {
        
        if (highlightView) {
            
            [highlightView removeFromSuperview], highlightView=nil;
            
        }
        
    }
    
    
}

- (void)setShared:(BOOL)shared {
    _shared = shared;
    
    _accessoryImageView.hidden = !shared;
    [self.titleLabel sizeToFit];
    
}

- (void)setLoading:(BOOL)loading {
    _loading = loading;
    
    self.userInteractionEnabled = !_loading;
    
    if (_loading) {
        
        if (!activityView) {
            
            UIActivityIndicatorView *view = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
            [self addSubview:view];
            [view startAnimating];
            view.layer.position = self.accessoryImageView.layer.position;
            self.activityView = view;

        }
        
        
    } else {
        
        if (activityView) {
            [activityView removeFromSuperview];
            self.activityView=nil;
        }
        
    }
    
}

@end