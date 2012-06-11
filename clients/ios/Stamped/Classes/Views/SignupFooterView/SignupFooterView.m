//
//  SignupFooterView.m
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import "SignupFooterView.h"
#import <CoreText/CoreText.h>

#define kCreateButtonTag 201

@interface STSignupTextLayer : CATextLayer
@property(nonatomic,assign) BOOL highlighted;
@end
@implementation STSignupTextLayer
@synthesize highlighted;

- (void)setup {
    
    CTFontRef ctFont = CTFontCreateWithName([[UIScreen mainScreen] scale] == 2.0 ? (CFStringRef)@"HelveticaNeue" : (CFStringRef)@"Helvetica", 12, NULL);
    CTFontRef boldFont = CTFontCreateCopyWithSymbolicTraits(ctFont, 0.0, NULL, kCTFontBoldTrait, kCTFontBoldTrait);
    NSMutableDictionary *boldStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)boldFont, kCTFontAttributeName, (id)[UIColor colorWithRed:0.478f green:0.611f blue:0.8f alpha:1.0f].CGColor, kCTForegroundColorAttributeName, nil];
    NSMutableDictionary *defaultStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)ctFont, kCTFontAttributeName, (id)[UIColor colorWithRed:0.6f green:0.6f blue:0.6f alpha:1.0f].CGColor, kCTForegroundColorAttributeName, nil];
    CFRelease(ctFont);
    CFRelease(boldFont);
    
    NSMutableAttributedString *string = [[NSMutableAttributedString alloc] initWithString:@"By tapping ‘Create Account’, you confirm that\nyou accept the terms of use and privacy policy." attributes:defaultStyle];
    [string setAttributes:boldStyle range:[string.string rangeOfString:@"terms of use"]];
    [string setAttributes:boldStyle range:[string.string rangeOfString:@"privacy policy"]];
    self.string = string;
    [string release];
    [defaultStyle release];
    [boldStyle release];
    
}

- (void)drawInContext:(CGContextRef)ctx {
    CGContextSetShadowWithColor(ctx, CGSizeMake(0.0f, 1.0f), 0.0f, [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor);
    [super drawInContext:ctx];
}

@end

@implementation SignupFooterView
@synthesize delegate;
@synthesize loading=_loading;

- (id)initWithFrame:(CGRect)frame {

    if ((self = [super initWithFrame:frame])) {
        
        STSignupTextLayer *layer = [STSignupTextLayer layer];
        layer.wrapped = YES;
        layer.contentsScale = [[UIScreen mainScreen] scale];
        layer.frame = CGRectMake(20.0f, 30.0f, self.bounds.size.width-40.0f, 40.0f);
        layer.backgroundColor = [UIColor clearColor].CGColor;
        layer.alignmentMode = @"center";
        [self.layer addSublayer:layer];
        [layer setup];

        UIImage *image = [UIImage imageNamed:@"signup_create_btn.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.tag = kCreateButtonTag;
        button.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        button.titleLabel.font = [UIFont boldSystemFontOfSize:14];
        button.titleLabel.shadowOffset = CGSizeMake(0.0f, -1.0f);
        button.frame = CGRectMake(10.0f, self.bounds.size.height - image.size.height, self.bounds.size.width-20.0f, image.size.height);
        [button setTitleShadowColor:[UIColor colorWithWhite:0.0f alpha:0.2f] forState:UIControlStateNormal];
        [button setTitle:NSLocalizedString(@"Create Account", @"Create Account") forState:UIControlStateNormal];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:button];
        _button = button;
        
        UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tapped:)];
        gesture.delegate = (id<UIGestureRecognizerDelegate>)self;
        [self addGestureRecognizer:gesture];
        [gesture release];
        
    }

    return self;
}

- (void)dealloc {
    self.delegate=nil;
    [super dealloc];
}


#pragma mark - Setters 

- (void)setLoading:(BOOL)loading {
    _loading = loading;
    
    _button.titleLabel.alpha = _loading ? 0.0f : 1.0f;
    self.userInteractionEnabled = !_loading;
    
    if (_loading) {
        
        if (!_activityView) {
            
            UIActivityIndicatorView *view = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleWhite];
            [self addSubview:view];
            [view startAnimating];
            view.layer.position = _button.layer.position;
            _activityView = view;
            
        }
        
        
    } else {
        
        if (_activityView) {
            [_activityView removeFromSuperview], _activityView=nil;
        }
        
    }
    
}


#pragma mark - Actions

- (void)buttonHit:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(signupFooterViewCreate:)]) {
        [self.delegate signupFooterViewCreate:self];
    }
    
}


#pragma mark - Gesture

- (BOOL)gestureRecognizerShouldBegin:(UIGestureRecognizer *)gestureRecognizer {
    
    UIView *view = [self viewWithTag:kCreateButtonTag];
    return !CGRectContainsPoint(view.frame, [gestureRecognizer locationInView:self]);
    
}

- (void)tapped:(UITapGestureRecognizer*)gesture {
    
    
    
}


@end
