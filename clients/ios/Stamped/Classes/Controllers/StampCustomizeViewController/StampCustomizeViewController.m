//
//  StampCustomizeViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "StampCustomizeViewController.h"
#import "StampColorPickerSliderView.h"

@interface StampCustomizeViewController ()
@property(nonatomic,readonly,retain) StampColorPickerSliderView *slider;
@property(nonatomic,readonly,retain) NSArray *colors;
- (void)updateStampView:(BOOL)animated;
@end

@implementation StampCustomizeViewController
@synthesize delegate;
@synthesize slider;
@synthesize colors=_colors;

- (id)initWithColors:(NSArray*)colors {
    if ((self = [super init])) {
        _colors = [colors retain];
    }
    return self;
}

- (id)init {
    if ((self = [super init])) {
        
        _colors = [[NSArray arrayWithObjects:[UIColor colorWithRed:0.0f green:0.290f blue:0.698f alpha:1.0f], [UIColor colorWithRed:0.0f green:0.3411f blue:0.819f alpha:1.0], nil] retain];
        
    }
    return self;
}

- (void)dealloc {
    
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Cancel", @"Cancel") style:UIBarButtonItemStyleBordered target:self action:@selector(cancel:)];
    self.navigationItem.leftBarButtonItem = button;
    [button release];
    
    button = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Done", @"Done") style:UIBarButtonItemStyleDone target:self action:@selector(done:)];
    self.navigationItem.rightBarButtonItem = button;
    [button release];
    
    if (!_stampView) {
        
        CALayer *layer = [CALayer layer];
        layer.contentsScale = [[UIScreen mainScreen] scale];
        layer.frame = CGRectMake((self.view.bounds.size.width-246.0f)/2, 10.0f, 246.0f, 246.0f);
        [self.view.layer addSublayer:layer];
        _stampView = layer;
        
    }
    
    if (!_sliderView) {
        
        StampColorPickerSliderView *view = [[StampColorPickerSliderView alloc] initWithFrame:CGRectMake(0.0f, self.view.bounds.size.height-160.0f, self.view.bounds.size.width, 160.0f)];
        view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleTopMargin;
        view.delegate = (id<StampColorPickerSliderDelegate>)self;
        [self.view addSubview:view];
        [view release];
        _sliderView = view;
        [view setColors:self.colors];
        
    }
    
    [self updateStampView:NO];
    
}

- (void)viewDidUnload {
    _stampView=nil;
    _sliderView=nil;
    [super viewDidUnload];
}

- (void)updateStampView:(BOOL)animated {
    
    UIGraphicsBeginImageContextWithOptions(_stampView.bounds.size, NO, 0);
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGRect rect = CGContextGetClipBoundingBox(ctx);
    
    CGContextTranslateCTM(ctx, 0.0f, rect.size.height);
    CGContextScaleCTM(ctx, 1.0f, -1.0f);
    
    CGContextClipToMask(ctx, rect, [UIImage imageNamed:@"stamp_270pt_texture.png"].CGImage);
    drawStampGradient([[_colors objectAtIndex:0] CGColor], [[_colors objectAtIndex:1] CGColor], ctx);
    UIImage *image = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    
    BOOL disabled = [CATransaction disableActions];
    [CATransaction setDisableActions:!animated];
    [CATransaction begin];
    [CATransaction setAnimationDuration:0.25f];
    _stampView.contents = (id)image.CGImage;
    [CATransaction commit];
    [CATransaction setDisableActions:disabled];

}


#pragma mark - Actions

- (void)done:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(stampCustomizeViewController:doneWithColors:)]) {
        [self.delegate stampCustomizeViewController:self doneWithColors:_colors];
    }
    
}

- (void)cancel:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(stampCustomizeViewControllerCancelled:)]) {
        [self.delegate stampCustomizeViewControllerCancelled:self];
    }
    
}


#pragma mark - StampColorPickerSliderDelegate

- (void)stampColorPickerSliderView:(StampColorPickerSliderView*)view pickedColors:(NSArray*)colors {
    [_colors release], _colors=nil;
    _colors = [colors retain];
    [self updateStampView:YES];
}


@end
