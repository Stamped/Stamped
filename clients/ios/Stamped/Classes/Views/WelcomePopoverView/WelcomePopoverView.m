//
//  WelcomePopoverView.m
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import "WelcomePopoverView.h"
#import "STBlockUIView.h"
#import <CoreText/CoreText.h>

@interface WelcomePopoverWelcomeView : UIView
@end

@interface WelcomePopoverOptionsView : UIView
- (id)initWithFrame:(CGRect)frame delegate:(id)delegate;
- (CATextLayer*)addTitle:(NSString*)title toButton:(UIButton*)button boldText:(NSString*)boldText;
@end

@implementation WelcomePopoverView

@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor clearColor];
        self.userInteractionEnabled = YES;
        
        UIScrollView *container = [[UIScrollView alloc] initWithFrame:CGRectInset(self.bounds, 7, 16)];
        container.pagingEnabled = YES;
        container.delegate = (id<UIScrollViewDelegate>)self;
        container.showsHorizontalScrollIndicator = NO;
        [self addSubview:container];
        [container release];
        _container = container;
        container.contentSize = CGSizeMake(container.frame.size.width*2, container.frame.size.height);
                
        WelcomePopoverWelcomeView *view = [[WelcomePopoverWelcomeView alloc] initWithFrame:_container.bounds];
        [_container addSubview:view];
        _welcomeView = view;
        [view release];
                
        if (!_optionsView) {
            
            CGRect frame = _container.bounds;
            frame.origin.x = frame.size.width;
            WelcomePopoverOptionsView *view = [[WelcomePopoverOptionsView alloc] initWithFrame:frame delegate:self];
            [_container addSubview:view];
            [view release];
            _optionsView = view;
            
         
        }
        /*
        UISwipeGestureRecognizer *gesture = [[UISwipeGestureRecognizer alloc] initWithTarget:self action:@selector(swiped:)];
        gesture.delegate = (id<UIGestureRecognizerDelegate>)self;
        gesture.direction = UISwipeGestureRecognizerDirectionLeft;
        [_welcomeView addGestureRecognizer:gesture];
        _swipe = gesture;
        [gesture release];
         */

    }
    return self;
}

- (void)dealloc {

    _welcomeView = nil;
    _swipe = nil;
    [super dealloc];
}

- (void)pushOptionsView {
    
    if (!_optionsView) {
        
        CGRect frame = _container.bounds;
        frame.origin.x = frame.size.width;
        WelcomePopoverOptionsView *view = [[WelcomePopoverOptionsView alloc] initWithFrame:frame delegate:self];
        [_container addSubview:view];
        [view release];
        _optionsView = view;
        
        UIButton *closeButton = [UIButton buttonWithType:UIButtonTypeCustom];
        [closeButton addTarget:self action:@selector(close:) forControlEvents:UIControlEventTouchUpInside];
        [closeButton setImage:[UIImage imageNamed:@"welcome_popover_close.png"] forState:UIControlStateNormal];
        
        frame = CGRectMake(-12.0f, -16.0f, 44.0f, 44.0f);
        frame = [self convertRect:frame toView:self.superview];
        closeButton.frame = frame;
        [self.superview addSubview:closeButton];

    }
    
    [UIView animateWithDuration:0.3f animations:^{
       
        CGRect frame = _welcomeView.frame;
        frame.origin.x = -_welcomeView.bounds.size.width;
        _welcomeView.frame = frame;
        
        frame = _optionsView.frame;
        frame.origin.x = 0.0f;
        _optionsView.frame = frame;
        
    } completion:^(BOOL finished) {
               
        _welcomeView.hidden = YES;
        
    }];
    
}

- (void)showOptionsView {
    
    _container.contentOffset = CGPointMake(_container.frame.size.width, 0.0f);
    
}


#pragma mark - Actions

- (void)close:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(welcomePopoverViewSelectedClose:)]) {
        [self.delegate welcomePopoverViewSelectedClose:self];
    }
    
}

- (void)login:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(welcomePopoverViewSelectedLogin:)]) {
        [self.delegate welcomePopoverViewSelectedLogin:self];
    }
    
}

- (void)email:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(welcomePopoverViewSelectedEmail:)]) {
        [self.delegate welcomePopoverViewSelectedEmail:self];
    }
}

- (void)twitter:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(welcomePopoverViewSelectedTwitter:)]) {
        [self.delegate welcomePopoverViewSelectedTwitter:self];
    }
    
}

- (void)facebook:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(welcomePopoverViewSelectedFacebook:)]) {
        [self.delegate welcomePopoverViewSelectedFacebook:self];
    }
}


#pragma mark - Gestures

- (void)swiped:(UISwipeGestureRecognizer*)gesture {
    
    [self pushOptionsView];
    [gesture setEnabled:NO];
    
}


#pragma mark - UIScrollViewDelegate 

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
    
    if (!_closeButton && scrollView.contentOffset.x >= scrollView.frame.size.width/2) {
        UIButton *closeButton = [UIButton buttonWithType:UIButtonTypeCustom];
        [closeButton addTarget:self action:@selector(close:) forControlEvents:UIControlEventTouchUpInside];
        [closeButton setImage:[UIImage imageNamed:@"welcome_popover_close.png"] forState:UIControlStateNormal];
        
        CGRect frame = CGRectMake(-12.0f, -16.0f, 44.0f, 44.0f);
        frame = [self convertRect:frame toView:self.superview];
        closeButton.frame = frame;
        [self.superview addSubview:closeButton];
        _closeButton = closeButton;
    }
    
}


@end


#pragma mark - WelcomePopoverWelcomeView

@implementation WelcomePopoverWelcomeView

- (id)initWithFrame:(CGRect)frame {
    if (self = [super initWithFrame:frame]) {
        
        self.backgroundColor = [UIColor whiteColor];
        
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"welcome_popover_title.png"]];
        [self addSubview:imageView];
        [imageView release];
        
        CGRect frame = imageView.frame;
        frame.origin.x = (self.bounds.size.width - frame.size.width)/2;
        imageView.frame = frame;
        
        CGFloat originY = CGRectGetMaxY(frame);
        
        imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"welcome_popover_images.png"]];
        [self addSubview:imageView];
        [imageView release];
        
        frame = imageView.frame;
        frame.origin.y = originY + 30.0f;
        frame.origin.x = (self.bounds.size.width - frame.size.width)/2;
        imageView.frame = frame;
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.textColor = [UIColor colorWithRed:0.204f green:0.447f blue:0.863f alpha:1.0f];
        label.font = [UIFont italicSystemFontOfSize:11];
        label.backgroundColor = [UIColor whiteColor];
        label.text = @"Swipe to continue";
        label.userInteractionEnabled = NO;
        [self addSubview:label];
        [label release];
        [label sizeToFit];
        
        originY = CGRectGetMaxY(frame) + 40.0f;
        
        frame = label.frame;
        frame.origin.x = floorf((self.bounds.size.width-frame.size.width)/2);
        frame.origin.y = originY;
        label.frame = frame;
        
        originY = CGRectGetMaxY(frame) + 8.0f;
        
        STBlockUIView *dots = [[STBlockUIView alloc] initWithFrame:CGRectMake((self.bounds.size.width-14.0f)/2, originY, 14.0f, 5.0f)];
        dots.backgroundColor = [UIColor whiteColor];
        [self addSubview:dots];
        [dots setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {

            [[UIColor colorWithRed:0.204f green:0.447f blue:0.863f alpha:1.0f] setFill];
            CGFloat height = rect.size.height;
            
            CGRect fillRect = CGRectMake(0.0f, 0.0f, height, height);
            CGContextAddPath(ctx, [UIBezierPath bezierPathWithRoundedRect:fillRect cornerRadius:height].CGPath);
            CGContextFillPath(ctx);
            
            CGContextSetAlpha(ctx, 0.6f);
            fillRect = CGRectMake(height + 4.0f, 0.0f,height, height);
            CGContextAddPath(ctx, [UIBezierPath bezierPathWithRoundedRect:fillRect cornerRadius:height].CGPath);
            CGContextFillPath(ctx);
            
        }];
        dots.userInteractionEnabled = NO;
        [dots release];

        
    }
    return self;
}

@end


#pragma mark - WelcomePopoverOptionsView

@implementation WelcomePopoverOptionsView

- (id)initWithFrame:(CGRect)frame delegate:(id)delegate {
    
    if ((self = [super initWithFrame:frame])) {
        self.backgroundColor = [UIColor whiteColor];
                
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"welcome_get_started.png"]];
        [self addSubview:imageView];
        [imageView release];
        
        CGRect frame = imageView.frame;
        frame.origin.x = (self.bounds.size.width - frame.size.width)/2;
        imageView.frame = frame;
        
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        UIImage *image = [UIImage imageNamed:@"welcome_facebook_btn.png"];
        [button addTarget:delegate action:@selector(facebook:) forControlEvents:UIControlEventTouchUpInside];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:image.size.width - 6.0f topCapHeight:0] forState:UIControlStateNormal];
        button.frame = CGRectMake(20.0f, 60.0f, self.bounds.size.width-40.0f, image.size.height);
        [self addSubview:button];
        CATextLayer *textLayer = [self addTitle:@"Sign in with Facebook" toButton:button boldText:@"Facebook"];
        textLayer.alignmentMode = @"left";
        frame = textLayer.frame;
        frame.origin.x = 60.0f;
        frame.origin.y -= 1.0f;
        textLayer.frame = frame;

        button = [UIButton buttonWithType:UIButtonTypeCustom];
        image = [UIImage imageNamed:@"welcome_twitter_btn.png"];
        [button addTarget:delegate action:@selector(twitter:) forControlEvents:UIControlEventTouchUpInside];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:image.size.width - 6.0f topCapHeight:0] forState:UIControlStateNormal];
        button.frame = CGRectMake(20.0f, 114.0f, self.bounds.size.width-40.0f, image.size.height);
        [self addSubview:button];
        textLayer = [self addTitle:@"Sign in with Twitter" toButton:button boldText:@"Twitter"];
        textLayer.alignmentMode = @"left";
        frame = textLayer.frame;
        frame.origin.x = 60.0f;
        frame.origin.y -= 1.0f;
        textLayer.frame = frame;
        
        UIFont *font = [UIFont systemFontOfSize:11];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(20.0f, floorf(CGRectGetMaxY(button.frame) + 10.0f), floorf(self.bounds.size.width-40.0f), font.lineHeight*2)];
        label.font = font;
        label.textColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f];
        label.numberOfLines = 2;
        label.textAlignment = UITextAlignmentCenter;
        label.lineBreakMode = UILineBreakModeWordWrap;
        label.text = @"We’ll never post anything to your\nFacebook or Twitter without your permission.";
        [self addSubview:label];
        [label release];
        
        CAShapeLayer *layer = [CAShapeLayer layer];
        layer.contentsScale = [[UIScreen mainScreen] scale];
        layer.fillColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor;
        layer.strokeColor = [UIColor colorWithRed:0.8509f green:0.8509f blue:0.8509f alpha:1.0f].CGColor;
        layer.lineDashPattern = [NSArray arrayWithObjects:[NSNumber numberWithFloat:1], [NSNumber numberWithFloat:2], nil];
        layer.frame = CGRectMake(24, CGRectGetMaxY(label.frame) + 16.0f, self.bounds.size.width - 48.0f, 1.0f);
        layer.path = [UIBezierPath bezierPathWithRect:layer.bounds].CGPath;
        layer.strokeEnd = .5;
        [self.layer addSublayer:layer];
        
        label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.font = [UIFont systemFontOfSize:11];
        label.backgroundColor = [UIColor whiteColor];
        label.textColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f];
        label.textAlignment = UITextAlignmentCenter;
        label.text = @"or";
        [label sizeToFit];
        [self addSubview:label];
        [label release];
        
        CGRect rect = label.frame;
        rect = CGRectInset(rect, -4, 0);
        rect.origin.x = floorf((self.bounds.size.width-rect.size.width)/2);
        rect.origin.y = floorf(layer.frame.origin.y - (rect.size.height/2));
        label.frame = rect;
        
        CGFloat originY = CGRectGetMaxY(label.frame)+10.0f;
        
        button = [UIButton buttonWithType:UIButtonTypeCustom];
        image = [UIImage imageNamed:@"welcome_email_btn.png"];
        [button addTarget:delegate action:@selector(email:) forControlEvents:UIControlEventTouchUpInside];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2)topCapHeight:0] forState:UIControlStateNormal];
        button.frame = CGRectMake(20.0f, originY, 150.0f, image.size.height);
        [self addSubview:button];
        [self addTitle:@"sign up with email" toButton:button boldText:@"email"];
        
        CGFloat originX = CGRectGetMaxX(button.frame) - 2.0f;
        button = [UIButton buttonWithType:UIButtonTypeCustom];
        image = [UIImage imageNamed:@"welcome_email_btn.png"];
        [button addTarget:delegate action:@selector(login:) forControlEvents:UIControlEventTouchUpInside];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        button.frame = CGRectMake(originX, originY, self.bounds.size.width-(originX+20.0f), image.size.height);
        [self addSubview:button];
        [self addTitle:@"login" toButton:button boldText:nil];

    }
    return self;
    
}

- (CATextLayer*)addTitle:(NSString*)title toButton:(UIButton*)button boldText:(NSString*)boldText {
    
    CTFontRef ctFont = CTFontCreateWithName([[UIScreen mainScreen] scale] == 2.0 ? (CFStringRef)@"HelveticaNeue" : (CFStringRef)@"Helvetica", 12, NULL);
    CTFontRef boldFont = CTFontCreateCopyWithSymbolicTraits(ctFont, 0.0, NULL, kCTFontBoldTrait, kCTFontBoldTrait);
    NSMutableDictionary *boldStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)boldFont, kCTFontAttributeName, (id)[UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor, kCTForegroundColorAttributeName, nil];
    
    NSMutableDictionary *defaultStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)ctFont, kCTFontAttributeName, (id)[UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor, kCTForegroundColorAttributeName, nil];
    
    CFRelease(ctFont);
    CFRelease(boldFont);
    
    NSMutableAttributedString *string = [[NSMutableAttributedString alloc] initWithString:title attributes:defaultStyle];
    if (boldText) {
        [string setAttributes:boldStyle range:[string.string rangeOfString:boldText]];
    }
    [defaultStyle release];
    [boldStyle release];
    
    CATextLayer *layer = [CATextLayer layer];
    layer.contentsScale = [[UIScreen mainScreen] scale];
    layer.frame = CGRectMake(floorf((button.bounds.size.width-140.0f)/2), floorf((button.bounds.size.height - 14)/2), 140.0f, 14);
    layer.backgroundColor = [UIColor clearColor].CGColor;
    layer.alignmentMode = @"center";
    layer.string = string;
    [string release];
    [button.layer addSublayer:layer];
    return layer;
    
    
}


@end
