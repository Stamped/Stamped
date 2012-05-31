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
@end

@implementation StampCustomizeViewController
@synthesize delegate;

- (id)initWithColors:(NSArray*)colors {
    if ((self = [super init])) {
        
    }
    return self;
}

- (id)init {
    if ((self = [super init])) {
        
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
    
    if (!_sliderView) {
        StampColorPickerSliderView *view = [[StampColorPickerSliderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 200.0f)];
        [self.view addSubview:view];
        [view release];
        _sliderView = view;
    }
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
}


#pragma mark - Actions

- (void)done:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(stampCustomizeViewController:doneWithColors:)]) {
        [self.delegate stampCustomizeViewController:self doneWithColors:nil];
    }
    
}

- (void)cancel:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(stampCustomizeViewControllerCancelled:)]) {
        [self.delegate stampCustomizeViewControllerCancelled:self];
    }
    
}


@end
