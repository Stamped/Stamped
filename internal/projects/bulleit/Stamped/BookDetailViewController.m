//
//  BookDetailViewController.m
//  Stamped
//
//  Created by Jake Zien on 9/11/11.
//  Copyright 2011 RISD. All rights reserved.
//

#import "BookDetailViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "Entity.h"

@interface BookDetailViewController ()
- (void)setupMainActionsContainer;
- (void)setupSectionViews;
@end

@implementation BookDetailViewController

@synthesize imageView         = imageView_;
@synthesize affiliateLogoView = affiliateLogoView_;


- (void)didReceiveMemoryWarning
{
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)showContents
{
  if (!entityObject_.author) 
    self.descriptionLabel.text = @"book";
  else
    self.descriptionLabel.text = [NSString stringWithFormat:@"by %@", entityObject_.author];
  
//  NSLog(@"%@", entityObject_);
  
  [self setupMainActionsContainer];
  [self setupSectionViews];
  
  if (entityObject_.image) {
    self.imageView.image = [UIImage imageWithData:[NSData dataWithContentsOfURL:
                                                   [NSURL URLWithString:entityObject_.image]]];
    self.imageView.hidden = NO;
  }
  
}

- (void)viewDidLoad {
  [super viewDidLoad];
  self.scrollView.contentSize = CGSizeMake(self.view.bounds.size.width, 480);
  self.mainActionButton.hidden = YES;
  self.mainActionLabel.hidden  = YES;
  self.mainActionsView.hidden  = YES;
  
}

- (void)viewDidUnload {
  self.mainContentView = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  self.categoryImageView.image = [UIImage imageNamed:@"sort_icon_book_0"];
  self.affiliateLogoView.image = [UIImage imageNamed:@"logo_amazon"];
  
  self.imageView.layer.shadowOffset  = CGSizeMake(0.0, 4.0);
  self.imageView.layer.shadowRadius  = 4.0;
  self.imageView.layer.shadowColor   = [UIColor blackColor].CGColor;
  self.imageView.layer.shadowOpacity = 0.33;
  self.imageView.frame = CGRectMake(self.imageView.frame.origin.x, self.imageView.frame.origin.y,
                                    self.imageView.frame.size.width, 144.0);
  self.imageView.contentMode = UIViewContentModeScaleAspectFit;
  
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}


- (IBAction)mainActionButtonPressed:(id)sender {
  [[UIApplication sharedApplication] openURL:
   [NSURL URLWithString:entityObject_.amazonURL]];
}



#pragma mark - Content Setup (data retrieval & logic to fill views)

- (void) setupMainActionsContainer {
  
  if (!entityObject_.amazonURL) {
    self.mainActionButton.hidden = NO;
    self.mainActionLabel.hidden  = NO;
    self.mainActionsView.hidden  = NO;
  }
  
  else self.mainContentView.frame = CGRectOffset(self.mainContentView.frame, 0, -CGRectGetHeight(self.mainActionsView.frame));
  
}


- (void) setupSectionViews {
  
  // Amazon Review
  if (entityObject_.desc) {
        
    [self addSectionWithName:@"Amazon Review" previewHeight:124.f];
    CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Amazon Review"];
    section.collapsedFooterText = [NSString stringWithFormat:@"read more"];
    section.expandedFooterText = @"read less";
    section.footerLabel.text = section.collapsedFooterText;
    [section addText:entityObject_.desc forKey:@"desc"];
    section.arrowView.frame = CGRectOffset(section.arrowView.frame, 
                                           [section.footerLabel.text sizeWithFont:section.footerLabel.font].width + 8.0, 0);
    
    self.mainContentView.hidden = NO;
  }
  
  
  // Details
  if (entityObject_.format || entityObject_.length || entityObject_.language || entityObject_.releaseDate ||
      entityObject_.publisher || entityObject_.isbn) {
    
    [self addSectionWithName:@"Details"];
    CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Details"];
    
    if (entityObject_.format && entityObject_.length)
      [section addPairedLabelWithName:@"Format:" 
                                value:[NSString stringWithFormat:@"%@, %@ pages", entityObject_.format, entityObject_.length] 
                               forKey:@"format"];
    else if (entityObject_.format)
      [section addPairedLabelWithName:@"Format:" 
                                value:entityObject_.format 
                               forKey:@"format"];
    else if (entityObject_.length)
      [section addPairedLabelWithName:@"Length:" 
                                value:[NSString stringWithFormat:@"%@ pages", entityObject_.length] 
                               forKey:@"length"];
    if (entityObject_.publisher)
      [section addPairedLabelWithName:@"Publisher:" 
                                value:entityObject_.publisher
                               forKey:@"publisher"];
    if (entityObject_.releaseDate)
      [section addPairedLabelWithName:@"Release Date:" 
                                value:entityObject_.releaseDate 
                               forKey:@"releaseDate"];
    if (entityObject_.language)
      [section addPairedLabelWithName:@"Language:" 
                                value:entityObject_.language 
                               forKey:@"language"];
    if (entityObject_.isbn)
      [section addPairedLabelWithName:@"ISBN:" 
                                value:entityObject_.isbn 
                               forKey:@"isbn"];
    
    self.mainContentView.hidden = NO;
  }
  
  
  // Stamped by  
  NSSet* stamps = entityObject_.stamps;
  
  if (stamps && stamps.count > 0)
  {
    [self addSectionStampedBy];
    self.mainContentView.hidden = NO; 
  }
  
}


@end
