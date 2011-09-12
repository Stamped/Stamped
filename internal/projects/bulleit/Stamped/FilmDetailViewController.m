//
//  BookDetailViewController.m
//  Stamped
//
//  Created by Jake Zien on 9/11/11.
//  Copyright 2011 RISD. All rights reserved.
//

#import "FilmDetailViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "Entity.h"

@interface FilmDetailViewController ()
- (void)setupMainActionsContainer;
- (void)setupSectionViews;
@end

@implementation FilmDetailViewController

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
  if (!entityObject_.length) 
    self.descriptionLabel.text = @"movie";

  else {
    NSNumber*  hours = [NSNumber numberWithFloat: entityObject_.length.floatValue / 3600.f];
    CGFloat fMinutes = hours.floatValue;
    hours = [NSNumber numberWithInt:floor(hours.floatValue)];
    
    while (fMinutes > 1)
      fMinutes -= 1.f;
    NSNumber* minutes = [NSNumber numberWithFloat:fMinutes * 60.f];
    
    self.descriptionLabel.text = [NSString stringWithFormat:@"%d hr %d min", hours.intValue, minutes.intValue];
  }
    
//  NSLog(@"%@", entityObject_);
  
  [self setupMainActionsContainer];
  [self setupSectionViews];
  
  //  if (entityObject_.artwork) {
  //    self.imageView.image  = entityObject_.artwork; 
  self.imageView.hidden = NO;
  //  }
  
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
  self.categoryImageView.image = [UIImage imageNamed:@"sort_icon_film_0"];
  self.affiliateLogoView.image = [UIImage imageNamed:@"logo_fandango"];
  
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
   [NSURL URLWithString:entityObject_.fandangoURL]];
}



#pragma mark - Content Setup (data retrieval & logic to fill views)

- (void) setupMainActionsContainer {
  
  if (entityObject_.fandangoURL) {
    self.mainActionButton.hidden = NO;
    self.mainActionLabel.hidden  = NO;
    self.mainActionsView.hidden  = NO;
  }
  
  else self.mainContentView.frame = CGRectOffset(self.mainContentView.frame, 0, -CGRectGetHeight(self.mainActionsView.frame));
  
}


- (void) setupSectionViews {
  
  // Synopsis
  if (entityObject_.desc) {
        
    [self addSectionWithName:@"Synopsis" previewHeight:124.f];
    CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Synopsis"];
    section.collapsedFooterText = [NSString stringWithFormat:@"read more"];
    section.expandedFooterText = @"read less";
    section.footerLabel.text = section.collapsedFooterText;
    [section addText:entityObject_.desc forKey:@"desc"];
    section.arrowView.frame = CGRectOffset(section.arrowView.frame, 
                                           [section.footerLabel.text sizeWithFont:section.footerLabel.font].width + 8.0, 0);
    
    self.mainContentView.hidden = NO;
  }
  
  
  // Information
  if (entityObject_.genre || entityObject_.cast || entityObject_.director || 
      entityObject_.inTheaters || entityObject_.releaseDate ) {
    
    [self addSectionWithName:@"Information"];
    CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Information"];
    
    if (entityObject_.cast)
      [section addPairedLabelWithName:@"Cast:" 
                                value:entityObject_.cast 
                               forKey:@"cast"];
    if (entityObject_.director)
      [section addPairedLabelWithName:@"Director:" 
                                value:entityObject_.director 
                               forKey:@"director"];
    if (entityObject_.genre)
      [section addPairedLabelWithName:@"Genres:" 
                                value:entityObject_.genre 
                               forKey:@"genre"];
    if (entityObject_.inTheaters)
      [section addPairedLabelWithName:@"In Theaters:" 
                                value:entityObject_.inTheaters.stringValue 
                               forKey:@"inTheaters"];
    if (entityObject_.releaseDate)
      [section addPairedLabelWithName:@"Open Date:" 
                                value:entityObject_.releaseDate
                               forKey:@"releaseDate"];

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
